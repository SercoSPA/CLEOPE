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

def sensing():
    start = widgets.DatePicker(
        description='Pick a date:',
        disabled=False)
    return start
    
def _b_(color="peachpuff"):
    b = widgets.Button(description="OK",layout=Layout(width='auto'))
    b.style.button_color = color
    return b

def _select_():
    stdate = sensing()
    btn_1 = _b_()
    box_1 = (HBox([stdate,btn_1],layout=Layout(width='65%', height='80px')))
    btn_2 = _b_()
    variable = _variable_()
    box_2 = HBox([variable,btn_2],layout=Layout(width='90%'))
    BOX = VBox([box_1,box_2],layout=Layout(width='auto', height='auto'))
    display(BOX)
    def sens_input(b):
        v = stdate.value
        dates = check_if_date_none(v)
        print("Sensing: %s"%dates)
        save_s(dates)       
    btn_1.on_click(sens_input)
    def var_input(b):
        var = convert_var(variable.value)
        print("Variable to monitor: %s" %var)
        save_var(var)
    btn_2.on_click(var_input)

def check_if_date_none(date):
    if date == None:
        print("None is not a date!")
        return datetime.strftime(datetime.now(),"%Y-%m-%d")
    else:
        return date
    
def check_sensing(date):
    if datetime.strptime(date,"%Y-%m-%d")>datetime.now() or datetime.strptime(date,"%Y-%m-%d")<datetime(2017,6,1):
        print("Wrong datetime range, fixing with the current month")
        return datetime.strftime(datetime.now(),"%Y-%m-%d") 
    else:
        return date     
    
def save_s(data):
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.DataFrame(np.nan,index=range(1),columns=["date"])
    df["date"] = data
    df.to_csv(file)    
   
def save_var(data):
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)
               
def convert_var(argument):
    switcher = {
        "Normalized_Difference_Vegetation_Index":"NDVI",
        "Frac_Absorbed_Photosynthetically_Active_Radiation_1km":"FAPAR",
        "Fraction_green_Vegetation_Cover_1km":"FCOVER",
        "Leaf_Area_Index_1km":"LAI",
    }
    return switcher.get(argument, "Invalid input")

def _variable_():
    options = ["Normalized_Difference_Vegetation_Index","Frac_Absorbed_Photosynthetically_Active_Radiation_1km","Fraction_green_Vegetation_Cover_1km","Leaf_Area_Index_1km"]
    m = widgets.Dropdown(options=options,layout=Layout(width='50%'),description="Variable")
    return m        

def read_var():
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'r') as fp:
        var = json.load(fp)
    return var

def read_sen():
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.read_csv(file)
    return df.date.values[0] # string

# monthly sampling for clands due to their non uniform sensing frenquence
# function goes one month back
def one_month_back(t):
    # t is a datetime object
    one_day = timedelta(days=1)
    one_month_back = t - one_day
    while one_month_back.month == t.month:  
        one_month_back -= one_day
    target_month = one_month_back.month
    while one_month_back.day > t.day:  
        one_month_back -= one_day
        if one_month_back.month != target_month:  # gone too far
            one_month_back += one_day
            break
    return one_month_back

# def add_months(t):
#     one_day = timedelta(days=1)
#     one_month_later = t + one_day
#     while one_month_later.month == t.month:  # advance to start of next month
#         one_month_later += one_day
#     target_month = one_month_later.month
#     while one_month_later.day < t.day:  # advance to appropriate day
#         one_month_later += one_day
#         if one_month_later.month != target_month:  # gone too far
#             one_month_later -= one_day
#             break
#     return one_month_later
        
def compose_pseudopath():
    root = "/mnt/Copernicus/Copernicus-land/"
    var = read_var()
    sens = check_sensing(read_sen())
    temp = datetime.strptime(sens,"%Y-%m-%d")
    now = datetime.strftime(temp,"/%Y/%m/")
    pseudopath = str(root)+str(var)+str(now)
    item = check_item()
    products = [p for p in glob.glob(pseudopath+"/**/"+item,recursive=True)]
    # check if products exists loop: goes one month back if no products are found during the current month
    if not products:
        old_date = temp
        while len(products) == 0:
#             print("No item matching datetime: %s >>> Going one month back"%datetime.strftime(old_date,"%Y-%b "))
            new_date = one_month_back(old_date) # one month back
            date = datetime.strftime(new_date,"/%Y/%m/")
            pseudopath = str(root)+str(var)+str(date)
            products = [p for p in glob.glob(pseudopath+"/**/"+item,recursive=True)]
            if products:
#                 print("Products found during: %s"%datetime.strftime(new_date,"%Y-%b "))
                sort_products = sorted(products)
                return sort_products[-1] # return the last datetime available for that variable
            else:
                old_date = new_date
                continue
    else:
        sort_products = sorted(products)
        return sort_products[-1] # return the last datetime available for that variable

def check_item():
    var = read_var()
    if var == "NDVI":
        return "c_gls_NDVI_*.nc"
    elif var == "FAPAR":
        return "c_gls_FAPAR_*.nc"
    elif var == "FCOVER":
        return "c_gls_FCOVER_*.nc"
    elif var == "LAI":
        return "c_gls_LAI_*.nc"
    else:
        print("No match found Error")
        return None

def dataset():
    variable = read_var()
    item = compose_pseudopath()
    ds = xarray.open_dataset(item)[str(variable)]
    return ds.isel(time=0),np.datetime_as_string(ds.time.data[0], timezone='UTC',unit='m')
    

