# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 09:56:19 2020

@author: GCIPOLLETTA
"""

import requests, json, shutil, os
import pandas as pd
import numpy as np
from tqdm import tqdm_notebook
from ipywidgets import widgets, Layout
from ipyleaflet import Map, DrawControl, Polygon

head = "https://catalogue.onda-dias.eu/dias-catalogue/Products?$search=%22"
tail = "%22&$format=json&orderby=creationDate%20asc"

head_count = "https://catalogue.onda-dias.eu/dias-catalogue/Products/$count?$search=%22"
tail_count = "%22"

missions = ["Sentinel-1","Sentinel-2","Sentinel-3","Sentinel-5 Precursor","Envisat","Landsat-*"]

# map maker
def define_map():
    m = Map(center=(40.853294, 14.305573), zoom=4,
            dragging=True,scroll_wheel_zoom=True,world_copy_jump=False)

    dc = DrawControl(
                 rectangle={'shapeOptions': {'color': 'dodgerblue'}},
                 circlemarker={},
                 )
    return m,dc
#marker={},
def update_Map(keys,polysel,df):
    polygon = Polygon(
    locations=make_locations(polysel),
    color="dodgerblue",
    fill_color="dodgerblue"
    )
    ind = [list(key)[1] for key in keys][0]
    objects = see_footprint(df,ind) # single footprint related to the (selected) product
    m = Map(center=centre(polysel), zoom=3,dragging=True,scroll_wheel_zoom=True) # initial map
    m.add_layer(polygon); # reference polygon (user input)
    for obj in objects:
        m.add_layer(obj);
    return m

def get(url):
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

def bounds_type(polysel):
    if polysel['type'] == "Polygon":
        return polysel["coordinates"][0], 0
    elif polysel['type'] == "LineString":
        return polysel["coordinates"], 1
    
def make_url(top,skip,polysel,product,sensing,printurl=False):
    # product è una lista [missione,ptype]
    # footprint url
    bounds, flag = bounds_type(polysel)
    if flag == 0:
        pp = [str(bounds[i][0])+"%20"+str(bounds[i][1]) for i in range(len(bounds))]
        tail_f = "footprint:%22Intersects(POLYGON(("+",".join(pp)+")))%22"+str(tail)+"&$top="+str(top)+"&$skip="+str(skip)
    else:
        pp = [str(bounds[i][0])+"%20"+str(bounds[i][1]) for i in range(len(bounds))]
        pp[-1] = pp[0]
        tail_f = "footprint:%22Intersects(POLYGON(("+",".join(pp)+")))%22"+str(tail)+"&$top="+str(top)+"&$skip="+str(skip)
    # other filters
    if sensing is None:
        if product[0] == "All":
            new_url = str(head)+str(tail_f) # solo fp
        else:
            if "All" in product[1]: # fp e missione 
                if product[0] in missions:
                    new_url = str(head)+"(%20platformName:"+str(product[0])+"%20)%20AND%20"+str(tail_f)
                else: # in questo caso cadono anche i cope 
                    new_url = str(head)+"(%20productMainClass:"+str(product[0])+"%20)%20AND%20"+str(tail_f)
            else: # fp e product type
                if product[0] == "Sentinel-1":
                    new_url = str(head)+"(%20(%20platformName:"+str(product[0])+"%20AND%20productType:*"+product[1]+"*%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head)+"(%20(%20platformName:"+str(product[0])+"%20AND%20productType:"+product[1]+"%20)%20)%20AND%20"+str(tail_f)
    else:
        if product[0] == "All":
            # fp e sensing
            new_url = str(head)+"(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20AND%20"+str(tail_f)
        else:
            if "All" in product[1]:
                # fp, sensing e missione
                if product[0] in missions:
                    new_url = str(head)+"(%20(%20(%20platformName:"+str(product[0])+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head)+"(%20(%20(%20productMainClass:"+str(product[0])+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
            else:
                # fp, sensing, missione e ptype
                if product[0] == "Sentinel-1":
                    new_url = str(head)+"(%20(%20(%20platformName:"+str(product[0])+"%20AND%20productType:*"+product[1]+"*%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head)+"(%20(%20(%20platformName:"+str(product[0])+"%20AND%20productType:"+product[1]+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
    if printurl == True:
        print(new_url)
    return new_url

def count(polysel,product,sensing):
    print("Searching for products...")
    bounds, flag = bounds_type(polysel)
    if flag == 0:
        pp = [str(bounds[i][0])+"%20"+str(bounds[i][1]) for i in range(len(bounds))]
        tail_f = "footprint:%22Intersects(POLYGON(("+",".join(pp)+")))%22"+str(tail_count)
    else:
        pp = [str(bounds[i][0])+"%20"+str(bounds[i][1]) for i in range(len(bounds))]
        pp[-1] = pp[0]
        tail_f = "footprint:%22Intersects(POLYGON(("+",".join(pp)+")))%22"+str(tail_count)
    if sensing is None:
        if product[0] == "All":
            new_url = str(head)+str(tail_f) # solo fp
        else:
            if "All" in product[1]: # fp e missione 
                if product[0] in missions:
                    new_url = str(head_count)+"(%20platformName:"+str(product[0])+"%20)%20AND%20"+str(tail_f)
                else: # in questo caso cadono anche i cope 
                    new_url = str(head_count)+"(%20productMainClass:"+str(product[0])+"%20)%20AND%20"+str(tail_f)
            else: # fp e product type
                if product[0] == "Sentinel-1":
                    new_url = str(head_count)+"(%20(%20platformName:"+str(product[0])+"%20AND%20productType:*"+product[1]+"*%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head_count)+"(%20(%20platformName:"+str(product[0])+"%20AND%20productType:"+product[1]+"%20)%20)%20AND%20"+str(tail_f)
    else:
        if product[0] == "All":
            # fp e sensing
            new_url = str(head_count)+"(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20AND%20"+str(tail_f)
        else:
            if "All" in product[1]:
                # fp, sensing e missione
                if product[0] in missions:
                    new_url = str(head_count)+"(%20(%20(%20platformName:"+str(product[0])+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head_count)+"(%20(%20(%20productMainClass:"+str(product[0])+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
            else:
                # fp, sensing, missione e ptype
                if product[0] == "Sentinel-1":
                    new_url = str(head_count)+"(%20(%20(%20platformName:"+str(product[0])+"%20AND%20productType:*"+product[1]+"*%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
                else:
                    new_url = str(head_count)+"(%20(%20(%20platformName:"+str(product[0])+"%20AND%20productType:"+product[1]+"%20)%20)%20AND%20(%20(%20beginPosition:"+str(sensing[0])+"%20AND%20endPosition:"+str(sensing[1])+"%20)%20)%20)%20AND%20"+str(tail_f)
    print(new_url)
    return requests.get(new_url).json() # number of products found (int)


def make_locations(polysel):
    p, flag = bounds_type(polysel)
    return [tuple([p[i][1],p[i][0]]) for i in range(len(p))]

def centre(polysel):
    bounds, flag = bounds_type(polysel)
    return tuple([bounds[0][1],bounds[0][0]])


def concat(dflist):
    len = dflist[0].shape[0] # uguale per tutti e uguale a top
    keys = [str(i) for i in range(len)]
    return pd.concat(dflist, keys=keys) 

def search(n,polysel,product,sensing):
    top = 100
    if n > 0:
        print("%d products found"%n)
        if (n/top) < 1:
            top = n
            nmax = int(n/top)
            total = nmax
        else:
            top = top
            nmax = int(n/top)
            total = nmax+1
        res = int(n-nmax*top) # residual results
        superdf = []
        with tqdm_notebook(total=total,desc="Loading query") as pbar:
            for i in range(nmax):  
                skip = i*top
                url = make_url(top,skip,polysel,product,sensing)
                dataframe = get(url) 
                superdf.append(dataframe)
#             print("Skipped %i"%skip)
                pbar.update(1)
            if res > 0:
                skip = nmax+res # update skip and repeat
                url = make_url(top,skip,polysel,product,sensing) 
                dataframe = get(url) 
                superdf.append(dataframe)
                pbar.update(1)
        df = concat(superdf)
        return df
    else:
        print("Warning: %d products found"%n)
        return None
    

def see_footprint(dataframe,i):
    colors = ["orange","forestgreen","blue","violet"]
    if "S1" in dataframe.iloc[i,1]:
        color = colors[0]
    elif "S2" in dataframe.iloc[i,1]:
        color = colors[1]
    elif "S3" in dataframe.iloc[i,1]:
        color = colors[2]
    elif "S5" in dataframe.iloc[i,1]:
        color = colors[3]
    else:
        color = "gray"
    objects = list() # list containing polygons 
    if "MULT" in dataframe.iloc[i,4]:
        tmp = dataframe.iloc[i,4][14:-1].split("))")[0:-1]
        if len(tmp) == 1: # multipolygon that is a polygon actually
            string = tmp[0][2:].split(",")[:-1]
            b = list()
            for s in string:
                temp = s.split(" ")
                tlist = [float(temp[-1]),float(temp[-2])] # fixed
                b.append(tuple(tlist))
            
            obj = Polygon(
                    locations=b,
                    color=color,
                    fill_color=color
                )
            objects.append(obj) # len 1
        else: # this is a true multipolygon 
            for k in range(len(tmp)): # instances help in finding how to split string
                if k > 0: 
                    string = tmp[k][3:].split(",")[:-1]
                    b = list()
                    for s in string:
                        temp = s.split(" ")
                        tlist = [float(temp[-1]),float(temp[-2])] # fixed
                        b.append(tuple(tlist))
                    obj = Polygon(
                            locations=b,
                            color=color,
                            fill_color=color
                        )
                    objects.append(obj)
                else:
                    string = tmp[k][2:].split(",")[:-1]
                    b = list()
                    for s in string:
                        temp = s.split(" ")
                        tlist = [float(temp[-1]),float(temp[-2])] # fixed
                        b.append(tuple(tlist))
                    obj = Polygon(
                            locations=b,
                            color=color,
                            fill_color=color
                        )
                    objects.append(obj)
    else: # this is a simple POLYGON
        string = dataframe.iloc[i,4][10:-2].split(",")[:-1]
        b = list()
        for s in string:
            temp = s.split(" ")
            tlist = [float(temp[-1]),float(temp[-2])] # fix 
            b.append(tuple(tlist))
        obj = Polygon(
                locations=b,
                color=color,
                fill_color=color
            )
        objects.append(obj)
    return objects

def createDF():
    fields = ["id","name","pseudopath","beginPosition","footprint","size","offline"] 
    return pd.DataFrame(columns=fields)

def save(item,dataframe):
    return dataframe.append(item)
    
def write(dataframe,filename=os.path.join(os.path.expanduser("~"),"outputs/saved_query.csv")):
    dataframe.to_csv(filename)
    print("Saved dataframe as %s\n"%filename)
    
def copy2(file,path=os.path.join(os.getcwd(),"outputs/")):
#     t = str(datetime.datetime.now())
    try:
        if "polygon" in file:
            shutil.copy2(file,path+"/polygon.json")
        else:
            shutil.copy2(file,path+"/list.txt")
        print("%s saved in %s"%(file,path))
        return 0
    except:
        print("Invalid file or destination set")
   
    
def select():
    mlist = ["All","Sentinel-1","Sentinel-2","Sentinel-3","Sentinel-5 Precursor","Envisat","Landsat-*"]
    mission = widgets.Dropdown(
        options=mlist,
        description='Mission:',
        layout=Layout(width="30%"),
        disabled=False)
    sensing_start = widgets.DatePicker(
        description = 'Sensed from:',
        disabled = False)
    sensing_stop = widgets.DatePicker(
        description = 'Sensed to:',
        disabled = False)
    return mission,sensing_start,sensing_stop
  
    
def warning(item):
    if item:
        print("Warning! This is an offline product. Check out ORDER notebook to trigger retrieval")

     
    