# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com

Main package aimed at CMEMS processing.
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
    """Create a widget to select sensing range

    Return: date pickers for sensing start and stop (ipywidgets objects)
    """
    start = widgets.DatePicker(
    description='Start Date')
    stop = widgets.DatePicker(
        description='End date')
    return start,stop

def _b_(color="skyblue"):
    """Define widgets button color

    Parameters:
        color (str): widget python color property; default: skyblue

    Return: styled button color (ipywidgets)
    """
    b = widgets.Button(description="OK",layout=Layout(width='auto'))
    b.style.button_color = color
    return b

def _select_():
    """Main selector for CMEMS datasets to be processed. Widgets objects (ipywidgets) are displayed on screen while selection inputs dumped into files.

    Return: None
    """
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
    """Check if sensing range selection is valid.

    Return: exit status (int)
    """
    tmp = np.array([start,stop])
    if tmp.all()==None:
        print("None is not a date!")
        return 1
    else:
        return 0

def sensing_range(start,stop):
    """Create a pandas dataframe from sensing range input selection, changing data format from datetime to str.

    Parameters:
        start (datetime): sensing range start (from function: sensing)
        stop (datetime): sensing range stop (from function: sensing)

    Return: sensing range information (pandas DataFrame)
    """
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
    """Save sensing range selection into file, named `out/dates.log` by default.

    Parameters:
        data (pandas DataFrame): sensing range information (from function: sensing_range)

    Return: None
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    data.to_csv(file)

def save_var(data):
    """Save CMEMS variable selection into file, named `out/variable.log` by default.

    Parameters:
        data (pandas DataFrame): CMEMS variable name information (from function: _variable_)

    Return: None
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def convert_var(argument):
    """Define CMEMS variable dictionary on options displayed via the widgets.

    Parameters:
        argument (str): input string selected

    Return: CMEMS product name property (str)
    """
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
    """Define CMEMS dataset variable dictionary on product name property.

    Parameters:
        argument (str): input product name

    Return: CMEMS dataset variable name property (str)
    """
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
    """Create a widget with CMEMS variables options.

    Return: widget (ipywidgets)
    """
    options = ["temperature","temperature_at_see_floor","horizontal_vel_3D","ice_concentration","mixed_layer_depth",
              "salinity","sea_surface_heigh"]
    m = widgets.Dropdown(options=options,layout=Layout(width='40%'),description="Variable")
    return m

def read_sen():
    """Read the sensing range input from the file named out/dates.log by default; from function: save_s

    Return: sensing range input selection (list)
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.read_csv(file)
    return [df.start.values[0],df.stop.values[0]]

def read_var():
    """Read the CMEMS variable name input from the file named out/variable.log by default; from function: save_var

    Return: variable name input selection (str)
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'r') as fp:
        var = json.load(fp)
    return var

def dates_list(freq="D"):
    """Sample the sensing range dates into regular intervals given an input frequency.

    Parameters:
        freq (str): sampling frequency; default is: `D` daily

        Allowed options are: `D` daily, `M` monthly, `W` weekly. If integer is provided too then sampling will be int*frequency.
        Warning: a white space must be left between the frequency option and the optional integer fraction of that.
        If the end date is in the future automatically fix with today date.
    """
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
    """Call the function: dates_list to compose ENS pseudopaths given the input sensing range and the CAMS product name.
    Default pseudopath field: `Copernicus-marine/GLOBAL_ANALYSIS_FORECAST_PHYS_001_015/MetO-GLO-PHYS-dm-`

    Parameters:
        freq (str): sampling frequency for function dates_list; default is: `D` daily

    Return: ENS pseudopaths (list)
    """
    root = "/mnt/Copernicus/Copernicus-marine/GLOBAL_ANALYSIS_FORECAST_PHYS_001_015/MetO-GLO-PHYS-dm-"
    dates = dates_list(freq=freq)
    var = read_var()
    return [str(root)+str(var)+str(d) for d in dates]


def _processing_(freq="D"):
    """Main function to open and read CMEMS datasets given all the user selections via ENS, calling function compose_pseudopath. Final dataset is concatenated and already sliced along dimensions:
        - time
        - depth (if present)

    Parameters:
        freq (str): sampling frequency for function dates_list; default is: `D` daily

    Return: CMEMS dataset (xarray)
    """
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
    """Check if depth dimension is present in the CMEMS data array.

    Return: exit status (bool)
    """
    if "depth" in image.dims:
        return True
    else:
        return False
