# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:47:00 2020

@author: GCIPOLLETTA
"""
import sys
sys.path.append("../")
import os, glob,json, datetime
from netCDF4 import Dataset
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm_notebook
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import imageio
# from IPython.core.display import display, HTML
from IPython.display import Image
import matplotlib.ticker as ticker
from ipywidgets import widgets, Layout

# cmap = sns.cubehelix_palette(light=1,as_cmap=True)
cmap = matplotlib.cm.magma_r

from holoviews import opts
import holoviews as hv
hv.extension('matplotlib')

gif_name = "pmovie.gif"

def query(file):
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    if "_local" in file:
        return [glob.glob(os.getcwd()+l,recursive=True)[0] for l in list] 
    elif "_remote" in file:
        nc = [p.split("/")[-1].split(".")[0]+".nc" for p in list]
        return [os.path.join(list[i],nc[i]) for i in range(len(list))]
    else:
        print("Error invalid filename.")
        return None
        

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

def plot(ds,key,file):
    # ["CO","HCHO","CH4","SO2","NO2","O3"] avaliable keys for S5P
    label = []
    images = []
    p = query(file)
    for i in range(len(ds)):
        temp = datetime.datetime.strptime(p[i].split("/")[-1].split("_")[-6],"%Y%m%dT%H%M%S")
        label = datetime.datetime.strftime(temp,"%b/%d/%Y")
        if key in ds[i].columns:
            images.append(hv.Scatter(ds[i]).opts(color=str(key),cmap=cmap, s=1,title=label,padding=0.05).hist(str(key)))
        i+=1
    return images

def read(bounds,file,verbose=True):
    products = query(file)
    latmin,latmax,lonmin,lonmax = bounds
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
    return [datetime.datetime.strftime(d,"%Y - %b - %d") for d in dates]

import ipywidgets as widgets
from IPython.display import display

# def multiplot(Variable):
#     ds = read(read_coordinates(),verbose=False)
#     labels = dates(query())
#     if ds == 1:
#         print("Unrecognized variable set, drop plotting")
#         return None
#     z = [ds[i].columns[-1] for i in range(len(ds))]
# #     seen = set()
# #     z = [x for x in z_tmp if x not in seen and not seen.add(x)] # remove repeated elements in list
#     val = np.arange(0,len(z),1)
#     map = {}
#     for key,values in zip(z,val):
#         map[key] = values
#     opts = z
#     display(hv.Scatter(ds[map[Variable]]).opts(color=Variable,cmap=cmap,s=50,
#                                                title=labels[map[Variable]],padding=0.05).hist(Variable))

# def variables():
#     df = read(read_coordinates())
#     z = [df[i].columns[-1] for i in range(len(df))]
# #     return z
#     seen = set()
#     return [x for x in z if x not in seen and not seen.add(x)]  
    
def units(file):
    products = query(file)
    for file in products:
        f = Dataset(file)
        if "L2__CO" in file:
            unit = f["PRODUCT"].variables["carbonmonoxide_total_column"].units
        elif "L2__HCHO" in file:
            unit = f["PRODUCT"].variables["formaldehyde_tropospheric_vertical_column"].units
        elif "L2__CH4" in file:
            unit = f["PRODUCT"].variables["methane_mixing_ratio"].units
        elif "L2__SO2" in file:
            unit = f["PRODUCT"].variables["sulfurdioxide_total_vertical_column"].units
        elif "L2__NO2" in file:
            unit = f["PRODUCT"].variables["nitrogendioxide_tropospheric_column"].units
        elif "L2__O3" in file:
            unit = f["PRODUCT"].variables["ozone_total_vertical_column"].units
        else:
            print("Key Error: unrecognized variable")
            return 1
    return unit    

def analysis(df,key,file):
    plt.ion() # mute plots 
    u = units(file) # pick up units from nc file
    data = pd.DataFrame(np.nan,columns=["date","val_u"],index=range(len(df)))
    days = [datetime.datetime.strptime(p.split("/")[-1].split("_")[-6],"%Y%m%dT%H%M%S") for p in query(file)]
    ndays = (days[-1]-days[0]).days
    for i in range(len(df)):
        filter = df[i]>0
        df[i].where(filter, inplace=True)
        data.iloc[i,1] = df[i][key].mean()
        data.iloc[i,0] = days[i]
    data.sort_values(by="date",inplace=True)
#     display(data)    
    xlims=(data.iloc[0,0],data.iloc[-1,0])
    fig,ax = plt.subplots(1,1,constrained_layout=False)
#     ax = sns.lineplot(x="date",y="val_u",data=data,color="Navy")
    if key == "NO2":
        variable = data.val_u*1E6
        ax.plot(data.date,variable,"-o")
        label = str(key)+" u"+str(u) 
        ylims = (variable.min()-variable.min()*0.1,variable.max()+variable.max()*0.1)
    else:
        ax.plot(data.date,data.val_u,"-o")
        label = str(key)+" "+str(u)
        ylims = (data.val_u.min()-data.val_u.min()*0.1,data.val_u.max()+data.val_u.max()*0.1)
    ax.set(xlim=xlims,ylim=ylims,xlabel="date",ylabel=label,title="Timeseries of %s mean value over selected area"%key)
    ax.grid(color="lavender")
    ax.set_xticks(days)
#     ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    fig.autofmt_xdate()
    return data

def plot_var(ds,key,file,create_movie=True):
    plt.ioff() # mute plots 
    dirName = 'plots'
    try:
        os.mkdir(dirName)
        print("Plots collected in %s"%dirName)
    except:
        print("\n")
    maxs = ([])
    variable = []
    labels = dates(query(file))
    for val in ds:
        if key == "NO2":
            z = val[key]*1E6
        else:
            z = val[key]
        maxs = np.append(maxs,z.max())
        variable.append(z.values)   
    max = maxs.max()
    normalize = matplotlib.colors.Normalize(vmin=0, vmax=max)
    bounds = np.linspace(0, max, 10)
    normalize_cb = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    if key == "NO2":
        cb_label = str(key)+" u"+str(units(file))
    else:
        cb_label = str(key)+" "+str(units(file))
    xlims = tuple(read_coordinates()[2:4])
    ylims = tuple(read_coordinates()[0:2])
    for i in range(len(ds)):
        fig,ax = plt.subplots(1,1,figsize=(8,6))
        im = ax.scatter(ds[i].lon.values, ds[i].lat.values, c=variable[i], s=5, cmap=cmap, norm=normalize)
        ax.set(xlim=xlims,ylim=ylims,xlabel='longitude',ylabel='latitude',title="%s"%labels[i])
        ax.minorticks_on()
        ax.set_aspect('equal', 'box')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(matplotlib.cm.ScalarMappable(cmap=cmap, norm=normalize_cb), cax=cax, orientation='vertical',label=cb_label,ticks=bounds,spacing='proportional',boundaries=bounds)
        fig.savefig(os.path.join(dirName,'plot_'+str(i)+".png"))
        fig.tight_layout()
        plt.close(fig)
    if create_movie==True:
        try:
            os.remove(gif_name)
        except:
            flag = 0
        images=[]
        imf = glob.glob(os.path.join(dirName,"plot_*.png"))
        imf.sort(key=os.path.getmtime)
        for im in imf:
            images.append(imageio.imread(im))
        imageio.mimsave(gif_name, images, duration=1)
        display_img()

def display_img(img_file=gif_name):
    with open(img_file,'rb') as f:
        display(Image(data=f.read(), format='png'))
    
def _list_():
    return glob.glob("list*",recursive=True)
    
def choose():
    mission = widgets.Dropdown(
    options=_list_(),
    description='Product:',
    layout=Layout(width="50%"),
    disabled=False,
    )
    display(mission)
    label = widgets.Label()
    btn = widgets.Button(description="CLICK to submit")
    display(btn)
    return mission,btn,label
    
    