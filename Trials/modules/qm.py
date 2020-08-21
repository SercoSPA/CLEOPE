# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA 
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com

Main module to send OData API queries for download and order instances.
Add this module to path: 
    import os, sys
    sys.path.append(os.path.join(os.path.expanduser("~"),"Trials/modules"))
    import qm
to easly perform queries via Jupyter Notebook.
"""
import requests, json, glob, os, zipfile, io, shutil, tarfile
import IPython
import pandas as pd
import numpy as np
import ipywidgets as widgets
import datetime, time
import threading
from IPython.display import display
from tqdm import tqdm_notebook
import warnings

du_thresh = 5 # GiB threshold 

def get(url):
    """Send and get the url to query products using OData API
    
    Parameters:
        url (str): OData url query
    
    Returns: query results (pandas dataframe)
    """
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
    """Send POST OData API to retrieve an archived product
    
    Parameters:
        username (str): ONDA username
        password (str): ONDA user password
        uuid (str): unique product identifier (from function: get_uuid)
    
    Return: OData POST request feedback (dict)    
    """
    if username and password:
        headers = {
            'Content-Type': 'application/json',
        }
        auth = (username, password)
        response = requests.post('https://catalogue.onda-dias.eu/dias-catalogue/Products('+uuid+')/Ens.Order',
                                 headers=headers, auth=auth)
        return response.json()

def get_uuid(product):
    """Get product unique identifier from product name
    
    Parameters:
        product (str): product name with its own extension explicit
    
    Returns: product uuid (str)
    Raise exception for invalid URLs.
    
    """
    if product.startswith("LC08"):
        if product.endswith(".tar.gz"):
            product = product
        else:
            product = product+".tar.gz"
    elif product.startswith("S"):
        if product.endswith(".zip"):
            product = product
        else:
            product = product+".zip"
    url = "https://catalogue.onda-dias.eu/dias-catalogue/Products?$search=%22"+str(product)+"%22&$top=10&$format=json"
    res = requests.get(url)
    try:
        return res.json()["value"][0]["id"]
    except:
        raise Exception("Invalid URL: Invalid product name.")

def get_my_product(product):
    """Search for products given the product name
    
    Parameters:
        product (str): product name
    
    Return: query results (pandas dataframe)
    Raise exception for invalid URLs. 
    """
    if product.endswith(".tar.gz"):
        product = product.split(".")[0]
    if product.startswith("S"):
        if product.endswith(".zip"):
            product = product
        else:
            product = product+".zip"
    url = "https://catalogue.onda-dias.eu/dias-catalogue/Products?$search=%22"+str(product)+"%22&$top=10&$format=json"
    res = requests.get(url)
    val = res.json()
    fields = ["id","name","pseudopath","beginPosition","footprint","size","offline"]
    try:
        dataframe = pd.DataFrame(np.nan,index=range(1), columns=fields)
        dataframe.iloc[0,0] = val["value"][0]["id"]
        dataframe.iloc[0,1] = val["value"][0]["name"]
        dataframe.iloc[0,2] = val["value"][0]["pseudopath"].split(",")[0]
        dataframe.iloc[0,3] = val["value"][0]["beginPosition"]
        dataframe.iloc[0,4] = val["value"][0]["footprint"]
        dataframe.iloc[0,5] = val["value"][0]["size"]
        dataframe.iloc[0,6] = val["value"][0]["offline"]
        return dataframe
    except:
        raise Exception("Empty dataframe: Invalid product name.")

def check_out_product(product):
    """Check if product has been properly restored in the ENS (ONDA Advanced API)
    
    Parameters:
        product (str): product name
    
    Return: exit status (int)
    """
#     time.sleep(1800) # sleep for 30 minutes untill order runs 
    pseudopath = get_my_product(product).iloc[0,2]
    link = "/mnt/Copernicus/"+pseudopath+"/"+product
    if os.path.exists(link):
        print("All done! Check out product:\n%s"%link)
        return 0
    else:
        print("Requested product not found.")
#         with open(os.path.join(os.getcwd(),"log.log"),"a+") as f:
#             f.write("\n")
#         f.close()
        return 1
    

# progress bar
def work(progress,delta):
    """Update a progress bar as a background process
    
    Parameters:
        progress (widget): tdqm notebook widget
        delta (datetime): time elapse
        
    Return: None    
    """
    total = int(delta)+1 
    for i in range(total):
        time.sleep(1) # tick upgrade in seconds
        progress.value = float(i+1)/total

# ordering API can manage thread instance 
def order(product, username, password):
    """Order an archived product in the background, displaying a progress bar updating untill complete restoration
    
    Parameters:
        product (str): product name
        username (str): ONDA username
        password (str): ONDA user password
    
    Return: product main attributes (pandas dataframe)
    """
    df = get_my_product(product)
    display(df)
    if df.iloc[0,6] == True:
        uuid = df.iloc[0,0]
        print("UUID to order: %s"%uuid)
        r = order_product(username,password,uuid)
        s = datetime.datetime.strptime(r["EstimatedTime"],'%Y-%m-%dT%H:%M:%S.%fZ')
        # removed additional 10s of waiting
        delta = datetime.datetime.timestamp(s)-datetime.datetime.timestamp(datetime.datetime.utcnow())#+600. # time elapse estimate to upgrade bar, 10 minutes added to wait for ENS refresh
        progress = widgets.FloatProgress(value=0.0, min=0.0, max=1.0, description="Ordering")
        thread = threading.Thread(target=work, args=(progress,delta,))
        tot_elaps_time = datetime.datetime.timestamp(s)#+600
        estimated_timeout = datetime.datetime.utcfromtimestamp(tot_elaps_time) 
        print("Instance is %s.\nEstimated time out %s UTC"%(r["Status"],estimated_timeout.strftime("%d-%b-%Y (%H:%M:%S.%f)")))
#         print("Instance is %s.\nEstimated time out %s UTC"%(r["Status"],datetime.datetime.strftime(s,'%H:%M:%S')))
#         print("Wait for further 10 minutes to be sure ENS is properly refreshed.")
        display(progress)
        thread.start()
    else:
        print("Warning! Products is already avaliable.\nCheck it out at:\n%s"%(os.path.join(df.iloc[0,2],product)))
    return df,delta
             
def pseudopath(dataframe,outfile="outputs/product_list_remote.txt"):
    """Compose the product pseudopath into ENS given product main attributes and dump the product list in a file.
    
    Parameters: 
        dataframe (pandas dataframe): product main attributes queried via OData
        outfile (str): full path of the output file location; default: outputs/product_list_remote.txt
        
    Return: pseudopaths list (list)
    """
    if dataframe.iloc[:,-1].values.any()==True:
        print("Warning! Some products in your dataframe are archived! Trigger an order request first. \nCheck out ORDER notebook to discover how to do it!\n") 
    pp = ["/mnt/Copernicus/"+os.path.join(dataframe.iloc[i,2],dataframe.iloc[i,1]) for i in range(dataframe.shape[0])]
    np.savetxt(outfile,np.vstack(pp),fmt="%s",newline="\n")
    print("Product list with pseudopaths saved as %s"%(os.path.join(os.getcwd(),outfile)))
    return pp
              
def read_product_list(file):
    """Read a custom product list and returns product pseudopaths into ENS.
    
    Parameters:
        file (str): full path of the input file list of products
    
    Return: single products main attributes (pandas dataframe)
    """
#     files = np.loadtxt(file,dtype=str)
    with open(file,"r") as f:
        data = f.read().splitlines()
        files = list(filter(None, data)) # remove newlines as empty strings 
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
    """Save a list with all the downloaded product location within users own workspace. The output list is generated in the current working directory by default and named 'list_local.txt' 
    
    Parameters:
        item (str): downloaded item full path location within CLEOPE workspace
        filename (str): output file full path location; default: ./list_local.txt
        
    Return: None    
    Note: items are appended to file per each download.
    """
    with open(filename,"a+") as f:
        f.write(item+"\n")
        print("%s updated"%filename)

def make_dir(dirname):
    """Create a brand new directory in the current working directory.
    
    Parameters:
        dirname (str): directory name
    
    Return: exit status
    """
    try:
        os.mkdir(dirname)
    except FileExistsError:
        return 0      
        
def download_item(url,auth,filename):
    """Helper method handling downloading large files from `url` to `filename`. 
    
    Parameters:
        url (str): an OData valid URL 
        auth (tuple): ONDA users own credentials
        filename (str): full path filename traking all the downloaded items
    
    Return: a pointer to `filename`
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

message = "CLEOPE free has a limited amount of resources available. To upgrade services under subscription please contact our ONDA Service Desk."

# download function available - use this to cache a product in the local_files directory 
def download(product,username,password):
    """Main function to download products via Jupyter Notebook within CLEOPE workspace. This is an alternative to ENS. A list traking all the downloaded files is automatically created in the working directory. Downloaded items are cached in a folder named `local_files` and placed into the /home/cleope-user own workspace.
    
    Parameters:
        product (str): product name
        username (str): ONDA user name
        password (str): ONDA user password
    
    Return: exit status (int)
    Raise an exception in case of disk full.
    
    """
    dest = os.path.join(os.path.join(os.path.expanduser("~"),"CLEOPE/local_files"))
    make_dir(dest)
    dataframe = get_my_product(product)
    uuid = dataframe.iloc[:,0].values[0]
    curl = "https://catalogue.onda-dias.eu/dias-catalogue/Products("+uuid+")/$value" 
    con = check_if_online(product,username,password) # check if online
    if con>0:
        print("Please wait until product restoration. Download will re-start automatically.")
        time.sleep(con+60) # Odata time lapse + 1 minute 
        # then check if restored
        df = get_my_product(product)
        if df["offline"].values==True:
            warnings.warn("Product %s is still archived. Something went wrong, retry the download in a few minutes."%product)
            return 1
    remove_item(dest,product) # check if products already exists in folder and delete it
    if check_size_disk():
        warnings.warn("%s"%message)
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
    """Remove a file or a directory and its related children if exists
    
    Parameters:
        item (str): full path location of file/directory to be removed
        
    Return: None    
    """
    file = glob.glob(item)
    if file:
        os.remove(file[0])
    else:
        print("%s not found"%item)

def check_size_disk():
    """Check available the disk space on cleope-users own home directory
    
    Return: exit status (bool)
    """
    user_home = os.path.expanduser("~")
    total, used, free = shutil.disk_usage(user_home)
    space = free//(2**30)
    if space>=du_thresh:
        return True
    else:
        return False

def remove_item(location,item): # location and product file
    """Remove a directory and its related children
    
    Parameters:
        location (str): full path of destination directory to be removed
        item (str): directory name 
    
    Return: None
    Raise exception if failing in removing the target directory.
    """
    file = glob.glob(os.path.join(location,item.split(".")[0]+'*'),recursive=True)
    if file:
        warnings.warn("Item: %s has already been downloaded."%item)
        if os.path.isdir(file[0]):
            try:
                shutil.rmtree(file[0])
            except:
                raise Exception("Exception occurred when trying to remove %s"%file)
        elif os.path.isfile(file[0]):
            os.remove(file[0])
        else:
            raise ValueError("Unrecognized item %s"%file[0])
    else:
        return
            
def download_list(file,username,password):
    """Call the function: download to download items recorsively from an input file list
    
    Parameters:
        file (str): input file list full path
        username (str): ONDA username
        password (str): ONDA user password
        
    Return: exit status (int)
    """
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    if list:
        for f in list:
            download(f,username,password)
        print("\n EOF: Good Job!")
        return 0
    else:
        warning.warn("Empty file list: %s"%file)

def check_if_online(product,username,password):
    """Call the function: order to retrieve an archived product when attempting a download it.
    
    Parameters:
        product (str): product name
        username (str): ONDA username
        password (str): ONDA user password
    
    Return: time elapse to restore product (float) if product is offline, otherwise an exit status (int)
    """
    df = get_my_product(product)
    if df["offline"].values==True:
        warnings.warn("Product %s is archived"%product)
        df,d = order(product,username,password)
        return d
    else:
        return 0
        
        