# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 09:56:19 2020

@author: GCIPOLLETTA
"""

import requests, json, glob, os, zipfile, io, time, shutil, tarfile
import IPython
import pandas as pd
import numpy as np
from time import time
import ipywidgets as widgets
import datetime, time
import threading
from IPython.display import display
from tqdm import tqdm_notebook

du_thresh = 3 # GiB threshold for a single product

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
    if product.endswith(".tar.gz"):
        product = product.split(".")[0]
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
    time.sleep(1800) # forces to sleep for 30 minutes untill order runs 
    pseudopath = get_my_product(product).iloc[0,2]
    link = "/mnt/Copernicus/"+pseudopath+"/"+product
    if os.path.exists(link):
        print("All done! Check out product:\n%s"%link)
    else:
        print("Requested product not found.")
#         with open(os.path.join(os.getcwd(),"log.log"),"a+") as f:
#             f.write("\n")
#         f.close()
        return 1
    

# progress bar
def work(progress,delta):
    total = int(delta)+1 
    for i in range(total):
        time.sleep(1) # tick upgrade in seconds
        progress.value = float(i+1)/total

# ordering API can manage thread instance 
def order(product, username, password):
    df = get_my_product(product)
    display(df)
    if df.iloc[0,6] == True:
        uuid = df.iloc[0,0]
        print("UUID to order: %s"%uuid)
        r = order_product(username,password,uuid)
        s = datetime.datetime.strptime(r["EstimatedTime"],'%Y-%m-%dT%H:%M:%S.%fZ')
        delta = datetime.datetime.timestamp(s)-datetime.datetime.timestamp(datetime.datetime.utcnow())+600. # time elapse estimate to upgrade bar, 10 minutes added to wait for ENS refresh
        progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0, description="Ordering")
        thread = threading.Thread(target=work, args=(progress,delta,))
        print("Instance is %s.\nEstimated time out %s UTC"%(r["Status"],datetime.datetime.strftime(s,'%H:%M:%S')))
        print("Wait for further 10 minutes to be sure ENS is properly refreshed.")
        display(progress)
        thread.start()
    else:
        print("Warning! Products is already avaliable.\nCheck it out at:\n%s"%(os.path.join(df.iloc[0,2],product)))
    return df
             
def pseudopath(dataframe):
    if dataframe.iloc[:,-1].values.any()==True:
        print("Warning! Some products in your dataframe are archived! Trigger an order request first. \nCheck out ORDER notebook to discover how to do it!\n") 
    pp = ["/mnt/Copernicus/"+os.path.join(dataframe.iloc[i,2],dataframe.iloc[i,1]) for i in range(dataframe.shape[0])]
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
              
def write_list(item,filename=os.path.join(os.getcwd(),"list_local.txt")):
    with open(filename,"a+") as f:
        f.write(item+"\n")
        print("%s updated"%filename)

def make_dir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        return 0      
        
def download_item(url,auth,filename):
    """
    Helper method handling downloading large files from `url` to `filename`. Returns a pointer to `filename`.
    auth tuple with ONDA credentials 
    """
    chunkSize = 1024
    r = requests.get(url,auth=auth,stream=True)
    with open(filename, 'wb') as f:
        pbar = tqdm_notebook(unit="B",total=int( r.headers['Content-Length'] ),desc="Downloading")
        for chunk in r.iter_content(chunk_size=chunkSize): 
            if chunk: # filter out keep-alive new chunks
                pbar.update (len(chunk))
                f.write(chunk)
    return filename

# download function available - use this to cache a product in the local_files directory 
def download(product,username,password):
    dest = os.path.join(os.path.expanduser("~"),"local_files") #os.path.join(os.path.expanduser("~"),
    make_dir(dest)
    dataframe = get_my_product(product)
    uuid = dataframe.iloc[:,0].values[0]
    curl = "https://catalogue.onda-dias.eu/dias-catalogue/Products("+uuid+")/$value" 
    if check_size_disk():
        file = download_item(curl,(username, password),os.path.join(dest,product))
        if product.endswith(".zip"):  
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(dest)
            zip_ref.close()
            print("%s successfully downloaded"%product)
            flag = True
        elif product.endswith(".tar.gz"): 
            tar = tarfile.open(os.path.join(dest,product), "r:gz")
            tar.extractall(os.path.join(dest,product.split(".")[0]+".ls8")) # extract landsat8 in a folder named after the product name 
            tar.close() 
            print("%s successfully downloaded"%product)
            flag = True
        elif product.endswith(".nc"):
            print("%s successfully downloaded"%product)
            flag = False
#         elif product.startswith("EN1_"): #! Envisat not supported 
#             with zipfile.ZipFile(file, 'r') as zip_ref:
#                 zip_ref.extractall(os.path.join(dest,product.split(".")[0]+".en1"))
#             zip_ref.close()
#             print("%s successfully downloaded"%product)
#             flag = True
        else:
            print("Product not recognized as .zip, .nc or .tar.gz. !Check out product name and specify extension.>\nPlease note that Envisat products are not supported by this function: download Envisat from ONDA Catalogue.<")
            return None
        # remove zip file after download 
        if flag:
            remove_zip(os.path.join(dest,product))
            file = glob.glob(os.path.join(dest,product.split(".")[0])+".*",recursive=True)
            if file:
                write_list(file[0])
            else:
                print("Unpacked %s not found"%product)
        else:
            file = glob.glob(os.path.join(dest,product))
            if file:
                write_list(file[0])
            else:
                print("%s not found"%product)
        return 0          
    else:
        raise MemoryError("Disk space lower than %d GiB\nRequest\n %s \nnot allowed."%(du_thresh,curl))
              
def remove_zip(item):
    file = glob.glob(item)
    if file:
        os.remove(file[0])
    else:
        print("%s not found"%item)

def check_size_disk():
    user_home = os.path.expanduser("~")
    total, used, free = shutil.disk_usage(user_home)
    space = free//(2**30)
    if space>=du_thresh:
        return True
    else:
        return False
    