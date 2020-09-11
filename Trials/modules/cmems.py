# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA

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

def _b_(color="skyblue",desc="OK"):
    """Define widgets button color

    Parameters:
        color (str): widget python color property; default: skyblue
        desc (str): button description; default: OK

    Return: styled button color (ipywidgets)
    """
    b = widgets.Button(description=desc,layout=Layout(width='auto'))
    b.style.button_color = color
    return b

def _select_(freq="D",variable="analysed_sst"):
    """Main selector for CMEMS datasets to be processed. Widgets objects (ipywidgets) are displayed on screen while selection inputs are dumped into files at path `out/` by default.
    
    Parameters:
        freq (str): sampling frequency; default is: `D` daily
        variable (str): variable extracted from the CMEMS NetCDF file

    Return: None
    """
    # sensing range
    start, stop = sensing()
    btn_1 = _b_(desc="Submit sensing")
    vbox1 = VBox([start,stop],layout=Layout(width='auto', height='80px'))
    box_1 = (HBox([vbox1,btn_1],layout=Layout(width='65%', height='80px')))
    display(box_1)
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
    btn_2 = _b_(color="Lavender",desc="START SEARCH")
    output = widgets.Output()
    display(btn_2,output)
    def proc_input(b):
        with output:
            print("\nSampling with frequency: %s"%freq)
            ims = _processing_(freq=freq,variable=variable)
            display(ims)
            ims.to_netcdf(os.path.join(dirName,"dataset.nc"))
    btn_2.on_click(proc_input)

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

def read_sen():
    """Read the sensing range input from the file named out/dates.log by default; from function: save_s

    Return: sensing range input selection (list)
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.read_csv(file)
    return [df.start.values[0],df.stop.values[0]]

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
    Default pseudopath field: `Copernicus-marine/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_005/METOFFICE-GLO-SST-L4-NRT-OBS-GMPE-V3`

    Parameters:
        freq (str): sampling frequency for function dates_list; default is: `D` daily

    Return: ENS pseudopaths (list)
    """
    root = "/mnt/Copernicus/Copernicus-marine/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_005/METOFFICE-GLO-SST-L4-NRT-OBS-GMPE-V3"
    dates = dates_list(freq=freq)
    return [str(root)+str(d) for d in dates]

def _processing_(freq="D",variable="analysed_sst"):
    """Main function to open and read CMEMS datasets given all the user selections via ENS, calling function compose_pseudopath. 
    
    Parameters:
        freq (str): sampling frequency for function dates_list; default is: `D` daily
        variable (str): variable to be extracted on dataset (among the possible choices allowed by the product type)

    Return: CMEMS variable dataset (xarray)
    """
    trg = compose_pseudopath(freq)
    products = []
    for t in trg: # check if pp exists
        for p in glob.glob(t+"*.nc",recursive=True):
            products.append(p)
    ds = [(xarray.open_dataset(p)[str(variable)]).isel(time=0) for p in products]
    # concatenate along time dimension
    try:
        return xarray.concat(ds, dim='time')
    except:
        raise Exception("xarray concat error on input files")

def read_ds(var="analysed_sst",path=os.path.join(dirName,"dataset.nc")):
    """Read the concatenated dataset created via the widget selection. The dataset is saved as out/dataset.nc automatically if no further path is provided.
    
    Parameters:
        var (str): variable of interest to be extracted from the xarray dataset; default `analysed_sst`
        path (str): full path of the dataset to be read; default `out/dataset.nc` created via the function _select_()
        
    Return: xarray dataset
    Raise Exception for errors in reading data.
    """
    try:
        return xarray.open_dataset(path)[var]
    except:
        raise Exception("Exception occurred when reading file %s"%path)
        
def table(path=os.path.join(dirName,"dataset.nc")):
    """Allows quick computation of the overall mean and standard deviation on the time-concatenated dataset, useful for timeseries analysis. By default the dataset saved as `out/dataset.nc` is loaded if any other path is provided.
    The input dataset must have the `time` dimension.
    
    Parameters:
        path (str): full path of the input dataset; default `out/dataset.nc`
        
    Return: pandas dataframe with mean and std values per each datetime
    Raise Exception for errors when reading the input dataset.
    """
    try:
        ds = xarray.open_dataset(path)
    except:
        raise Exception("Error occurred when loading %s"%path)
    df = pd.DataFrame(np.nan,columns=["time","mean","std"],index=range(ds.time.shape[0]))
    for i in range(ds.time.shape[0]):
        df.iloc[i,0] = ds["time"].isel(time=i).data
        df.iloc[i,1] = ds["analysed_sst"].isel(time=i).mean()
        df.iloc[i,2] = ds["analysed_sst"].isel(time=i).std()
    return df
