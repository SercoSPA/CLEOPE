import pandas as pd
import os, glob, datetime, json
import rasterio 
import numpy as np
from tqdm import tqdm_notebook
import matplotlib.pyplot as plt
from ipywidgets import widgets, Layout
import datetime
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib 
from netCDF4 import Dataset
from dateutil import parser

cmap = sns.color_palette("RdYlGn",256)

def products(file=os.path.join(os.getcwd(),"list.txt")):
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
        return list

def dates(products):
    dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S") for p in products]
    return [datetime.datetime.strftime(d,"%b/%d/%Y") for d in dates]

def bounds():
    try:
        with open('polygon.json', 'r') as fp:
            polysel = json.load(fp)
            return tuple([polysel["coordinates"][0][0][0],polysel["coordinates"][0][0][1],polysel["coordinates"][0][2][0],polysel["coordinates"][0][1][1]])
    except:
        return None


def water(olcis,imgname,var="tsm_nn"):
    opt = ["tsm_nn","chl_oc4me","iwv"]
    inf = np.array([0,1E-1,1])
    bmap = {}; nmap = {}
    for key,values in zip(opt,inf):
        bmap[key] = values
    u = ["g m-3","mg(ch a) m-3","kg m-2"]
    for key,values in zip(opt,u):
        nmap[key] = values
    if var not in opt:
        print("Water: variable name error")
        return None
    f_geo = glob.glob(olcis+"/**/geo_coordinates.nc",recursive=True)
    if f_geo:
        f_geo = f_geo[0]
    else:
        print("Product not found\n")
        return 1
    try:
        geoc = Dataset(f_geo)
    except:
        print("Error while reading file %s"%f_geo)
        return 1
    lat = geoc.variables["latitude"][::]
    long = geoc.variables["longitude"][::]
    tile = (long.min(),long.max(),lat.min(),lat.max())
    f_w = glob.glob(olcis+"/**/"+str(var)+".nc",recursive=True)[0]
    try:
        nc = Dataset(f_w)
    except:
        print("Error while reading file %s"%f_w)
        return 1
    _temp = olcis.split("/")[-1]
    _date = _temp.split("_")[-11]
    _obj = parser.parse(_date)
    title = _obj.strftime("%b %d %Y %H:%M")
    cmap = matplotlib.cm.jet
    fig,ax = plt.subplots(1,1,sharey=True,figsize=(10,6))
    varname = var.upper()
    temp = nc.variables[varname][::] 
    im = ax.imshow(temp,cmap=cmap,extent=(long.min(),long.max(),lat.min(),lat.max()))
    ax.set(xlabel='longitude',ylabel="latitude",title=title)
    max = np.max(temp.max())
    bounds = np.linspace(bmap[var],max,256)
    norm = matplotlib.colors.BoundaryNorm(boundaries=bounds,ncolors=256) #
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="5%",pad=0.05)
    cb = matplotlib.colorbar.ColorbarBase(cax,cmap=cmap,norm=norm,orientation="vertical")
    cb.set_label(nmap[var])
    plt.show()
    wd = os.getcwd()
    dirName = "plots"
    try:
        os.mkdir(os.path.join(wd,dirName))
        print("Created directory %s collecting plots" %os.path.join(wd,dirName))
    except FileExistsError:
        print("Directory %s collects plots" %os.path.join(wd,dirName))
    dest = os.path.join(wd,dirName)
    fig.savefig(dest+"/"+str(imgname)+".png",dpi=150)
    print("%s saved in %s"%(imgname,dest))
    plt.close()

def land(olcis,imgname,var="otci"):
    opt = ["otci","ogvi"]
    if var not in opt:
        print("Land: variable name error")
        return None
    f_geo = glob.glob(olcis+"/**/geo_coordinates.nc",recursive=True)
    if f_geo:
        f_geo = f_geo[0]
    else:
        print("Product not found\n")
        return 1
    try:
        geoc = Dataset(f_geo)
    except:
        print("Error while reading file %s"%f_geo)
        return 1
    lat = geoc.variables["latitude"][::]
    long = geoc.variables["longitude"][::]
    tile = (long.min(),long.max(),lat.min(),lat.max())
    f = glob.glob(olcis+"/**/"+str(var)+".nc",recursive=True)[0]
    try:
        nc = Dataset(f)
    except:
        print("Error while reading file %s"%f)
        return 1
    _temp = olcis.split("/")[-1]
    _date = _temp.split("_")[-11]
    _obj = parser.parse(_date)
    title = _obj.strftime("%b %d %Y %H:%M")
    cmap = matplotlib.cm.terrain_r
    fig,ax = plt.subplots(1,1,sharey=True,figsize=(10,6))
    varname = var.upper()
    temp = nc.variables[varname][::] 
    im = ax.imshow(temp,cmap=cmap,extent=(long.min(),long.max(),lat.min(),lat.max()))
    ax.set(xlabel='longitude',ylabel="latitude",title=title)
    max = np.max(temp.max()); min = np.min(temp.min())
    bounds = np.linspace(min,max,256)
    norm = matplotlib.colors.BoundaryNorm(boundaries=bounds,ncolors=256) #
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="5%",pad=0.05)
    cb = matplotlib.colorbar.ColorbarBase(cax,cmap=cmap,norm=norm,orientation="vertical")
    cb.set_label(var)
    plt.show()
    wd = os.getcwd()
    dirName = "plots"
    try:
        os.mkdir(os.path.join(wd,dirName))
        print("Created directory %s collecting plots" %os.path.join(wd,dirName))
    except FileExistsError:
        print("Directory %s collects plots" %os.path.join(wd,dirName))
    dest = os.path.join(wd,dirName)
    fig.savefig(dest+"/"+str(imgname)+".png",dpi=150)
    print("%s saved in %s"%(imgname,dest))
    plt.close()    
   
