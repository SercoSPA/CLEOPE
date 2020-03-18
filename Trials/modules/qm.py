# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 09:56:19 2020

@author: GCIPOLLETTA
"""

import requests, json, glob, os, zipfile, io, time
import IPython
import pandas as pd
import numpy as np
from time import time
import ipywidgets as widgets
import datetime, time
import threading
from IPython.display import display
from tqdm import tqdm_notebook

def get(url):
    res = requests.get(url)
    val = res.json()
    n = len(val["value"])
    fields = ["id","name","pseudopath","beginPosition","footprint","size","offline"]
    dataframe = pd.DataFrame(np.nan,index=range(n), columns=fields)
    for i in range(n):
        dataframe.iloc[i,0] = val["value"][i]["id"]
        dataframe.iloc[i,1] = val["value"][i]["name"]
        dataframe.iloc[i,2] = val["value"][i]["pseudopath"].split(",")[0]
        dataframe.iloc[i,3] = val["value"][i]["beginPosition"]
        dataframe.iloc[i,4] = val["value"][i]["footprint"]
        dataframe.iloc[i,5] = val["value"][i]["size"]
        dataframe.iloc[i,6] = val["value"][i]["offline"]
    return dataframe

def order_product(username, password, uuid):
    if username and password:
        headers = {
            'Content-Type': 'application/json',
        }
        auth = (username, password)
        response = requests.post('https://catalogue.onda-dias.eu/dias-catalogue/Products('+uuid+')/Ens.Order',
                                 headers=headers, auth=auth)
        return response.json()

def get_uuid(product):
    product = product if product.endswith(".zip") else product + ".zip"
    url = "https://catalogue.onda-dias.eu/dias-catalogue/Products?$search=%22"+str(product)+"%22&$top=10&$format=json"
    res = requests.get(url)
    return res.json()["value"][0]["id"]


def get_my_product(product):
    #product = product if (product.endswith(".zip") or product.endswith("nc")) else product + ".zip"
    url = "https://catalogue.onda-dias.eu/dias-catalogue/Products?$search=%22"+str(product)+"%22&$top=10&$format=json"
    res = requests.get(url)
    val = res.json()
    fields = ["id","name","pseudopath","beginPosition","footprint","size","offline"]
    dataframe = pd.DataFrame(np.nan,index=range(1), columns=fields)
    dataframe.iloc[0,0] = val["value"][0]["id"]
    dataframe.iloc[0,1] = val["value"][0]["name"]
    dataframe.iloc[0,2] = val["value"][0]["pseudopath"].split(",")[0]
    dataframe.iloc[0,3] = val["value"][0]["beginPosition"]
    dataframe.iloc[0,4] = val["value"][0]["footprint"]
    dataframe.iloc[0,5] = val["value"][0]["size"]
    dataframe.iloc[0,6] = val["value"][0]["offline"]
    return dataframe

def check_out_product(product):
#     st = time.time()
    time.sleep(1800) # forces to sleep for 30 minutes - as requested by IVV
#     print("%.3f"%(time.time()-st))
    pseudopath = get_my_product(product).iloc[0,2]
    link = "/mnt/Copernicus/"+pseudopath+"/"+product
    #list = glob.glob(link+"*",recursive=True)
    list = glob.glob(link+"/*.SAFE",recursive=True)
    if list:
        print("All done! Check out product:\n%s"%link)
    else:
        print("Requested product not found.")
        with open(os.path.join(os.getcwd(),"log.log"),"a+") as f:
            f.write("\n")
        f.close()
        return 1
    
# patch 
def download(product,username,password):
    dataframe = get_my_product(product)
    uuid = dataframe.iloc[:,0].values[0]
    curl = "https://catalogue.onda-dias.eu/dias-catalogue/Products("+uuid+")/$value"
    st = time.time()
    print("Download started")
    r = requests.get(curl,auth=(username, password))
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()
    print("Download completed in %.3f s"%(time.time()-st))
    print("Find your product:\n%s"%os.path.join(os.getcwd(),str(dataframe.iloc[:,1].values[0])))
    return None
    
# progress bar
def work(progress,delta):
    total = int(delta)+1 
    for i in range(total):
        time.sleep(1) # tick upgrade in seconds
        progress.value = float(i+1)/total

# ordering API
def order(product, username, password):
    df = get_my_product(product)
    display(df)
    if df.iloc[0,6] == True:
        uuid = df.iloc[0,0]
        print("UUID to order: %s"%uuid)
        r = order_product(username,password,uuid)
        s = datetime.datetime.strptime(r["EstimatedTime"],'%Y-%m-%dT%H:%M:%S.%fZ')
        delta = datetime.datetime.timestamp(s)-datetime.datetime.timestamp(datetime.datetime.utcnow()) # time elapse estimate to upgrade bar
        progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0, description="Ordering")
        thread = threading.Thread(target=work, args=(progress,delta,))
        print("Instance is %s.\nEstimated time out %s UTC"%(r["Status"],datetime.datetime.strftime(s,'%H:%M:%S')))
        display(progress)
        thread.start()
    else:
        print("Warning! Products is already avaliable.\nCheck it out at:\n%s"%(os.path.join(df.iloc[0,2],product)))
    return df
             
def pseudopath(dataframe):
    if dataframe.iloc[:,-1].values.any()==True:
        print("Warning! Product in your dataframe is archived, tagged with the offline status. You cannot find it at its standard pseudopath but order it first. \nCheck out ORDER notebook to discover how to trigger an order!\n") 
    pp = ["/mnt/Copernicus/"+os.path.join(dataframe.iloc[i,2],dataframe.iloc[i,1]) for i in range(dataframe.shape[0])]
    print("Find out the path into ENS:")
    print("\n".join(pp))
    np.savetxt("resources/pseudopath_file.txt",np.vstack(pp),fmt="%s",newline="\n",header="pseudopath list",comments="#")
    print("Pseudopaths saved in %s"%(os.path.join(os.getcwd(),"resources/pseudopath_file.txt")))
    return pp
              
def read_product_list(file="resources/product_list_trial.txt"):
    files = np.loadtxt(file,dtype=str)
    l = list()
    with tqdm_notebook(total=len(files),desc="Waiting for ONDA catalogue") as pbar:
        for f in files:
            dataframe = get_my_product(f)
            l.append(dataframe)
            pbar.update(1)
    dataframe = pd.concat(l,ignore_index=True)
    display(dataframe)
    return dataframe
              
              
              
              