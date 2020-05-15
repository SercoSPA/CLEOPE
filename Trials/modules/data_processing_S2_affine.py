import os, sys, xarray, datetime
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
import rasterio.warp
import matplotlib.pyplot as plt
import warnings

epsg = {'init': 'EPSG:4326'}
lc = ((864.7-664.6)/(1613.7-664.6))*10.

def product(file):
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]

def product_level(item):
    if "MSIL2A" in item:
        return True
    elif "MSIL1C" in item:
        return False
    else:
        raise ValueError("%s: Unrecognized S2 product type"%item)
        
def rgb_bands(item):
    msi = product_level(item)
    products = []
    if msi: # L2A
        for path in Path(item).rglob('*B0[2-4]_10m.jp2'): 
            products.append(str(path))
    else: # L1C
        for path in Path(item).rglob('*B0[2-4].jp2'): 
            products.append(str(path))
    return sorted(products,reverse=True) # ordered bands

def false_rgb_bands(item): # false color 
    products = []
    if (item.find('MSIL2A') != -1):
        bands = ["*B03_10m.jp2","*B04_10m.jp2","*B08_10m.jp2"]
        for b in bands:
            for path in Path(item).rglob(b):
                products.append(str(path))
    else:
        bands = ["*B03.jp2","*B04.jp2","*B08.jp2"]
        for b in bands:
            for path in Path(item).rglob(b):
                products.append(str(path))
    if len(products)>3: # check
        warnings.warn('Too many bands opened\n',products)
    return sorted(products,reverse=True)

def falseir_rgb_bands(item):
    products = []
    if (item.find('MSIL2A') != -1):
        bands = ["*B12_20m.jp2","*B11_20m.jp2","*B05_20m.jp2"]
        for b in bands:
            for path in Path(item).rglob(b):
                products.append(str(path))
    else:
        bands = ["*B12.jp2","*B11.jp2","*B05.jp2"]
        for b in bands:
            for path in Path(item).rglob(b):
                products.append(str(path))
    if len(products)>3: # check
        warnings.warn('Too many bands opened\n',products)
    return sorted(products,reverse=True)

# find all bands given resolution
def bands(item,res='10m'):
    msi = product_level(item)
    products = []
    string = '*_'+str(res)+'.jp2'
    if msi: # L2A
        for path in Path(item).rglob(string): 
            products.append(str(path))
    else: # L1C
        for path in Path(item).rglob('*.jp2'): 
            products.append(str(path))
    return sorted(products) # ordered bands

def ndwi_bands(item):
    msi = product_level(item)
    products = []
    if msi: # L2A
        for path in Path(item).rglob('*B0[3-8]_10m.jp2'): 
            products.append(str(path))
        products = sorted(products)
    else: # L1C
        for path in Path(item).rglob('*B0[3-8].jp2'): 
            products.append(str(path))
        products = sorted(products)
    return [products[0],products[-1]]
   
def affine(b):
    # S2 bands share the same geometry
    ds = xarray.open_rasterio(b).isel(band=0)
    ra = rasterio.open(b,driver='JP2OpenJPEG') 
    # affine transformation to lat and lon
    xt, yt = rasterio.warp.transform(src_crs=ra.crs, dst_crs=rasterio.crs.CRS(epsg), xs=ds.x,ys=ds.y)
    lon, lat = np.array(xt), np.array(yt) 
    return lon,lat

def reproject(bands):
    """ordered bands list as input
    """
    ds = [xarray.open_rasterio(b).isel(band=0) for b in bands] # open data arrays as they are
    lon,lat = affine(bands[0]) # S2 tiles share equal geocoding, one band is sufficient for affine transformation
    newds = [xarray.DataArray(data=ds[i].data,coords=[lat,lon],dims=["y","x"]) for i in range(len(bands))] # new data array transformed
    conc_new = xarray.concat(newds,pd.Index([i for i in range(len(bands))])) # concat along channel
    conc_new = conc_new.rename({"concat_dim":"channel"})
    del newds,lat,lon
    xoff, yoff = np.around(conc_new.x.data[0],1), np.around(conc_new.y.data[0],1)
    conc_new.attrs = {'transform':(10.0, 0.0, xoff, 0.0, -10.0, yoff), # (a,b,xoff,d,e,yoff)
                      'crs':list(epsg.values())[0]} 
    return conc_new

def clip(ds,bounds,plot=False):
    xmin,xmax,ymin,ymax = bounds
    mask_lon = (ds.x >= xmin) & (ds.x <= xmax)
    mask_lat = (ds.y >= ymin) & (ds.y <= ymax)
    clip_ds = ds.where(mask_lon & mask_lat, drop=True)
    if plot == True:
        fig,ax = plt.subplots(1,1)
        clip_ds.plot.imshow('x','y',robust=True,ax=ax)
        plt.show()
        return clip_ds, fig
    else:
        return clip_ds
         
def ratio(da):
    return (da.isel(channel=0).astype(float)-da.isel(channel=1).astype(float))/(da.isel(channel=0).astype(float)+da.isel(channel=1).astype(float))

def dates(products):
    if isinstance(products,list):
        dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S") for p in products]
        return [datetime.datetime.strftime(d,"%b/%d/%Y") for d in dates]
    else:
        dates = datetime.datetime.strptime(products.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S")
        return [datetime.datetime.strftime(dates,"%b/%d/%Y")]
