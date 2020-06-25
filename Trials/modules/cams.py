# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA 
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com
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

def gmt_widget():
    options = ["GMT 00:00","GMT 12:00"]
    return [widgets.Checkbox(value=False,description=opt) for opt in options] 

def _b_(color="lightgreen"):
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
    btn_3 = _b_()
    wlist = gmt_widget()
    box_3 = HBox([wlist[0],wlist[1],btn_3],layout=Layout(width='auto'))
    BOX = VBox([box_1,box_2,box_3],layout=Layout(width='auto', height='auto'))
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
    def time_inputs(b):  
#         print("GMT: %s %s"%(wlist[0].value,wlist[1].value))
        flag_gmt = check_gmt(wlist[0].value,wlist[1].value)
        if flag_gmt:
            save_gmt([True,True])
        else:
            print("GMT set")
            save_gmt([wlist[0].value,wlist[1].value])
    btn_3.on_click(time_inputs)

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
        "nitrogen_dioxide": "tcno2",
        "carbon_monoxide": "tcco",
        "sulfur_dioxide":"tcso2",
        "methane":"tc_ch4",
        "ethane":"tc_c2h6",
        "propane":"tc_c3h8",
        "isoprene":"tc_c5h8",
        "hydrogen_peroxide":"tc_h2o2",
        "formaldehyde":"tchcho",
        "nitric_acid":"tc_hno3",
        "nitrogen_monoxide":"tc_no",
        "hydroxide":"tc_oh",
        "peroxyacyl_nitrates":"tc_pan",
    }
    return switcher.get(argument, "Invalid input")
    
def _variable_():
    options = ["nitrogen_dioxide","carbon_monoxide","sulfur_dioxide","methane","ethane","propane","isoprene",
               "hydrogen_peroxide","formaldehyde","nitric_acid","nitrogen_monoxide","hydroxide","peroxyacyl_nitrates"]
    m = widgets.Dropdown(options=options,layout=Layout(width='30%'),description="Element")
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

def read_gmt():
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"gmt.log")
    data = pd.read_csv(file,header=0,index_col=0)
    if data.values.all():
        return ["*000000_*.nc","*120000_*.nc"]
    else:
        if data.iloc[0,0] == True:
            return ["*000000_*.nc"]
        else:
            return ["*120000_*.nc"]

def _processing_(freq="D"):
    gmt = read_gmt()
    if len(gmt)>1:
        files00 = [glob.glob(path+gmt[0],recursive=True) for path in compose_pseudopath(freq=freq)] 
        files12 = [glob.glob(path+gmt[1],recursive=True) for path in compose_pseudopath(freq=freq)]
        products = []
        for f,g in zip(files00,files12):
            if f and g:
                products.append(f[0])
                products.append(g[0])
    else:
        products = [glob.glob(path+gmt[0],recursive=True)[0] for path in compose_pseudopath(freq=freq)]
    var = read_var()
    xlist = [(xarray.open_dataset(p)[str(var)]).isel(time=0) for p in products] 
    image = xarray.concat(xlist, dim='time')
    return image
    

def local_processing(var=None):
    products = glob.glob("local_files/z_cams*.nc",recursive=True)
    varlist = [p.split("_")[-1].split(".")[0] for p in products]
    if varlist[1:] == varlist[:-1]:
        var = varlist[0]
        xlist = [(xarray.open_dataset(p)[str(var)]).isel(time=0) for p in products] 
        image = xarray.concat(xlist, dim='time')
        return image
    else:
        print("Different CAMS products found in your dataset folder. Please provide a variable to monitor as var argument of this function, e.g. var='tcco'")
        return None       