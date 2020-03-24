# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:10:29 2020

@author: GCIPOLLETTA 
"""
from ipywidgets import widgets, interact, Layout, interactive, VBox
from IPython.display import display
import pandas as pd
import numpy as np
import json, os, glob, xarray
from datetime import datetime, timedelta
# from IPython.core.display import display, HTML
# import imageio

# Create output directory
dirName = 'out'
try:
    os.mkdir(dirName)
except FileExistsError:
    flag = 1

limit = 30 # limit on the product number 
    
def sensing():
    start = widgets.DatePicker(
    description='Start Date')
    stop = widgets.DatePicker(
        description='End date')
    return start,stop

def _select_():
    # sensing range
    start, stop = sensing()
    display(VBox([start,stop],layout=Layout(width='50%', height='80px')))
    btn = widgets.Button(description="Submit range")
    display(btn)    
    def inputs(b):  
        print("Sensing range from %s to %s"%(start.value,stop.value))
        sens = sensing_range(start.value,stop.value)
        save_s(sens)
    btn.on_click(inputs)
    variable = _variable_()
    display(variable)
    btn_p = widgets.Button(description="Submit variable")
    display(btn_p) 
    def var_input(b):
        var = convert_var(variable.value)
        print("Variable to monitor: %s" %var)
        save_var(var)
    btn_p.on_click(var_input)

def sensing_range(start,stop):
    df = pd.DataFrame(np.nan,index=range(1),columns=["start","stop"])
    if np.logical_or(start==None,stop==None) == True:
        return None
    else:
        str_start = start.strftime("%Y/%m/%d")
        str_stop = stop.strftime("%Y/%m/%d")
        df["start"] = str_start
        df["stop"] = str_stop
        return df
    
def save_s(data):
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    data.to_csv(file)
    
def save_var(data):
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)
        
def convert_var(input):
    if input == "carbon_monoxide":
        var = "tcco"
    elif input == "nitrogen_dioxide":
        var = "tcno2"
    else:
        return None
    return var
        
def _variable_():
    options = ["nitrogen_dioxide","carbon_monoxide"]
    m = widgets.Dropdown(options=options,layout=Layout(width='20%'))
    return m        

def read_sen():
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.read_csv(file)
    return [df.start.values[0],df.stop.values[0]]

def read_var():
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'r') as fp:
        var = json.load(fp)
    return var
       
def dates_list(freq="D"):
    # select sampling frequency
    temp = freq.split()
    if len(temp)>1:
        m = int(freq.split()[0])
        if freq.split()[1] == "D":
            timestep = m
        elif freq.split()[1] == "W":
            timestep = m*7
        elif freq.split()[1] == "M":
            timestep = m*30
    else:
        if freq == "D":
            timestep = 1
        elif freq == "W":
            timestep = 7
        elif freq == "M":
            timestep = 30
#     print(timestep)
    list = read_sen()
    if list:
        start,stop = list[0],list[1]
        start_date = datetime.strptime(start,"%Y/%m/%d")
        end_date = datetime.strptime(stop,"%Y/%m/%d")
        if end_date > datetime.now():
            delta = datetime.now()-start_date # if date in the future put today
            last = datetime.now().strftime("/%Y/%m/%d/")
            nmax = delta.days
            print("Warning! End date is in the future - Fixed with today date: %s"%last)
        else:
            delta = end_date-start_date
            nmax = delta.days + timestep
            if (end_date+timedelta(timestep))>datetime.now():
                nmax = delta.days
#                 last = datetime.now().strftime("/%Y/%m/%d/")
        path_date = []
        for single_date in (start_date + timedelta(n) for n in range(0,nmax,timestep)):
            path_date.append(single_date.strftime("/%Y/%m/%d/")) 
        try:
            path_date.append(last)
        except NameError:
            last = None
        if len(path_date)>limit:
            return path_date[-limit:]
        else:
            return path_date
    else:
        print("Input must be a list")
        return None

def compose_pseudopath(freq="D"):
    root = "/mnt/Copernicus/Copernicus-atmosphere/ANALYSIS/SURFACE_FIELDS/"
    dates = dates_list(freq=freq)
    var = read_var()
    return [str(root)+str(var)+str(d) for d in dates]
        
def _processing_(freq="D"):
    files00 = [glob.glob(path+"*000000_*.nc",recursive=True) for path in compose_pseudopath(freq=freq)] 
    files12 = [glob.glob(path+"*120000_*.nc",recursive=True) for path in compose_pseudopath(freq=freq)]
    products = []
    for f,g in zip(files00,files12):
        if f and g:
            products.append(f[0])
            products.append(g[0])
# define 00 or 12 *120000_* #######!!!!!
#     products = [f[0] for f in files if f]
    var = read_var()
    xlist = [np.log10(xarray.open_dataset(p)[str(var)]).isel(time=0) for p in products] # log10 scale
    image = xarray.concat(xlist, dim='time')
    return image
    
       