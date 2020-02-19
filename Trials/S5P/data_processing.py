# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:47:00 2020

@author: GCIPOLLETTA
"""

import os, glob,json, datetime
from netCDF4 import Dataset
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm_notebook

cmap = sns.cubehelix_palette(light=1,as_cmap=True)

from holoviews import opts
import holoviews as hv
hv.extension('matplotlib')

# def query(f="saved_query.csv"):
#     data = pd.read_csv(f,index_col=0,header=0)
#     if data.iloc[:,-1].values.any() == True:
#         print("Warning! Some products in your dataframe are archived, tagged with the offline status.\nCheck out ORDER notebook to discover how to trigger an order!")
#     nc = [data.iloc[i,1].split(".")[0]+".nc" for i in range(data.shape[0])]
#     return ["/mnt/Copernicus/"+os.path.join(data.iloc[i,2],data.iloc[i,1])+"/"+nc[i] for i in range(data.shape[0])]

def products(file=os.path.join(os.getcwd(),"list.txt")):
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
        return list
    
def query():
    pro = products()
    nc = [p.split("/")[-1].split(".")[0]+".nc" for p in pro]
    return [os.path.join(pro[i],nc[i]) for i in range(len(pro))]

def read_coordinates(path=os.getcwd(),filename='polygon.json'):
    file = glob.glob(os.path.join(path,filename),recursive=True)[0]
    with open(file, 'r') as fp:
        polysel = json.load(fp)
    if polysel["type"] == "Polygon":
        bounds = polysel["coordinates"][0]
    elif polysel["type"] == "LineString":
        bounds = polysel["coordinates"] 
    bounds_stack = np.column_stack(bounds)
    return [bounds_stack[1].min(),bounds_stack[1].max(),bounds_stack[0].min(),bounds_stack[0].max()]

def plot(ds,key):
    # ["CO","HCHO","CH4","SO2","NO2","O3"] avaliable keys for S5P
    label = []
    images = []
    p = query()
    for i in range(len(ds)):
        temp = datetime.datetime.strptime(p[i].split("/")[-1].split("_")[-6],"%Y%m%dT%H%M%S")
        label = datetime.datetime.strftime(temp,"%b/%d/%Y")
        if key in ds[i].columns:
            images.append(hv.Scatter(ds[i]).opts(color=str(key),cmap=cmap, s=1,title=label,padding=0.05).hist(str(key)))
        i+=1
    return images

def read(bounds,verbose=True):
    latmin,latmax,lonmin,lonmax = bounds
    products = query()
    datasets = list()
    #with tqdm_notebook(total=len(products),desc="Reading...") as pbar:
    for file in products:
        try:
            f = Dataset(file)
            lon = f["PRODUCT"].variables["longitude"][0,::]
            lat = f["PRODUCT"].variables["latitude"][0,::]
            if "L2__CO" in file:
                var = f["PRODUCT"].variables["carbonmonoxide_total_column"][0,::]
                key = "CO"
            elif "L2__HCHO" in file:
                var = f["PRODUCT"].variables["formaldehyde_tropospheric_vertical_column"][0,::]
                key = "HCHO"
            elif "L2__CH4" in file:
                var = f["PRODUCT"].variables["methane_mixing_ratio"][0,::]
                key = "CH4"
            elif "L2__SO2" in file:
                var = f["PRODUCT"].variables["sulfurdioxide_total_vertical_column"][0,::]
                key = "SO2"
            elif "L2__NO2" in file:
                var = f["PRODUCT"].variables["nitrogendioxide_tropospheric_column"][0,::]
                key = "NO2"
            elif "L2__O3" in file:
                var = f["PRODUCT"].variables["ozone_total_vertical_column"][0,::]
                key = "O3"
            else:
                print("Key Error: unrecognized variable")
                return 1
            b = np.ma.where(np.logical_and(np.logical_and(lat>=latmin,lat<=latmax),np.logical_and(lon>lonmin,lon<lonmax)))
            A = np.ma.zeros((len(b[0]),3))
            A[:,1] = lat[b]  #y
            A[:,0] = lon[b]  #x
            A[:,2] = var[b]  #z
            dataframe = pd.DataFrame(data=A,columns=["lon","lat",key])
            datasets.append(dataframe)
        except:
            if verbose == True:
                print("Error occurred when opening file: %s"%file) 
                continue
    return datasets # all datasets related to product file list

def dates(products):
    dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[-6],"%Y%m%dT%H%M%S") for p in products]
    return [datetime.datetime.strftime(d,"%b/%d/%Y") for d in dates]

import ipywidgets as widgets
from IPython.display import display

def multiplot(Variable):
    ds = read(read_coordinates(),verbose=False)
    labels = dates(query())
    if ds == 1:
        print("Unrecognized variable set, drop plotting")
        return None
    z = [ds[i].columns[-1] for i in range(len(ds))]
#     seen = set()
#     z = [x for x in z_tmp if x not in seen and not seen.add(x)] # remove repeated elements in list
    val = np.arange(0,len(z),1)
    map = {}
    for key,values in zip(z,val):
        map[key] = values
    opts = z
    display(hv.Scatter(ds[map[Variable]]).opts(color=Variable,cmap=cmap, s=1, title=labels[map[Variable]],padding=0.05).hist(Variable))

def variables():
    df = read(read_coordinates())
    z = [df[i].columns[-1] for i in range(len(df))]
#     return z
    seen = set()
    return [x for x in z if x not in seen and not seen.add(x)]  
    
    
