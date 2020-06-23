# -*- coding: utf-8 -*-
"""
Created on Thu Apr 02 09:31:07 2020

@author: GCIPOLLETTA 
"""
from ipywidgets import widgets, interact, Layout, interactive, VBox, HBox
from IPython.display import display
import pandas as pd
import numpy as np
import json, os, glob, xarray
from datetime import datetime, timedelta

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

def _b_(color="skyblue"):
    b = widgets.Button(description="OK",layout=Layout(width='auto'))
    b.style.button_color = color
    return b

def _select_():
    # sensing range
    start, stop = sensing()
    btn_1 = _b_()
    vbox1 = VBox([start,stop],layout=Layout(width='auto', height='80px'))
    box_1 = (HBox([vbox1,btn_1],layout=Layout(width='65%', height='80px')))
    btn_2 = _b_()
    variable = _variable_()
    box_2 = HBox([variable,btn_2],layout=Layout(width='90%'))
    BOX = VBox([box_1,box_2],layout=Layout(width='auto', height='auto'))
    display(BOX)
    def sens_input(b):
        print("Sensing date range from %s to %s"%(start.value,stop.value))
        check = check_sensing(start.value,stop.value)
        if check:
            print("DatePicker Error")
            stop.value = datetime.now()
            start.value = datetime.now()-timedelta(1)
        sens = sensing_range(start.value,stop.value)
        save_s(sens)
    btn_1.on_click(sens_input)
    def var_input(b):
        var = convert_var(variable.value)
        print("Variable to monitor: %s" %var)
        save_var(var)
    btn_2.on_click(var_input)

def check_sensing(start,stop):
    tmp = np.array([start,stop])
    if tmp.all()==None:
        print("None is not a date!")
        return 1
    else:
        return 0    

def check_gmt(var1,var2):
    tmp = np.array([var1,var2])
    if tmp.any() == False:
        print("GMT not set - selected both options")
        return 1
    else:
        return 0
    
def save_gmt(list):
    data = pd.DataFrame(np.array(list).reshape(1,2),columns=["GMT00","GMT12"])
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"gmt.log")
    data.to_csv(file)

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
               
def convert_var(argument):
    switcher = {
        "temperature":"TEM",
        "temperature_at_see_floor":"BED",
        "horizontal_vel_3D":"CUR",
        "ice_concentration":"ICE",
        "mixed_layer_depth":"MLD",
        "salinity":"SAL",
        "sea_surface_heigh":"SSH",
    }
    return switcher.get(argument, "Invalid input")

def switch2attr(argument):
    switcher = {
        "TEM":"thetao",
        "BED":"bottomT",
        "CUR":None,
        "ICE":"siconc",
        "MLD":"mlotst",
        "SAL":"so",
        "SSH":"zos",
    }
    return switcher.get(argument, "Invalid input")


def _variable_():
    options = ["temperature","temperature_at_see_floor","horizontal_vel_3D","ice_concentration","mixed_layer_depth",
              "salinity","sea_surface_heigh"]
    m = widgets.Dropdown(options=options,layout=Layout(width='40%'),description="Variable")
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
    root = "/mnt/Copernicus/Copernicus-marine/GLOBAL_ANALYSIS_FORECAST_PHYS_001_015/MetO-GLO-PHYS-dm-"
    dates = dates_list(freq=freq)
    var = read_var()
    return [str(root)+str(var)+str(d) for d in dates]


def _processing_(freq="D"):
    trg = compose_pseudopath(freq)
    products = []
    for t in trg: # check if pp exists
        for p in glob.glob(t+"*.nc",recursive=True):
            products.append(p)
    variable = switch2attr(read_var())
    if variable is None:
        ds = [(xarray.open_dataset(p)).isel(time=0) for p in products] # 3D case for velocities  
    else:
        ds = [(xarray.open_dataset(p)[str(variable)]).isel(time=0) for p in products] 
    # concatenate along time dimension
    image = xarray.concat(ds, dim='time')
    tmax = len(image)
    # check if depth dimension exists
    if check_if_depth(image):
        dmax = image.depth.shape[0]
        return image.isel(time=slice(0,tmax,1),depth=slice(0,dmax,1)) # return a slice in time and depth
    else:
        return image.isel(time=slice(0,tmax,1)) # return time series slice
        

def check_if_depth(image):
    if "depth" in image.dims:
        return True
    else:
        return False

