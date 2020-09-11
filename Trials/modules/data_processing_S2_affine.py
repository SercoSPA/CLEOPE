# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA

Main module aimed at S2 data handling and visualisation.
"""
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
    """Read an input product list returning a list of products suitable for reading.

    Parameters:
        file (str): full path of the input file product list

    Return: lines of file read (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]

def product_level(item):
    """Check for S2 product type. This information will change the relative path to images.

    Parameters:
        item (str): full path to S2 products location

    Return: exit status (bool)
    Raise ValueError for Unrecognized product types
    """
    if "MSIL2A" in item:
        return True
    elif "MSIL1C" in item:
        return False
    else:
        raise ValueError("%s: Unrecognized S2 product type"%item)

def rgb_bands(item):
    """Search for the full path location of S2 R, G and B bands, at 10m resolution by default.
    Equivalent whether using ENS or local downloaded products within users own workspace.

    Parameters:
        item (str): full path to S2 products location

    Return: list of full path S2 `.jp2` bands sorted by decreasing wavelength
    """
    msi = product_level(item)
    products = []
    if msi: # L2A
        for path in Path(item).rglob('*B0[2-4]_10m.jp2'):
            products.append(str(path))
    else: # L1C
        for path in Path(item).rglob('*B0[2-4].jp2'):
            products.append(str(path))
    return sorted(products,reverse=True) # ordered bands

def false_rgb_bands(item):
    """Search for the full path location of S2 B03, B04 and B08 bands at 10m resolution by default.
    Equivalent whether using ENS or local downloaded products within users own workspace.

    Parameters:
        item (str): full path to S2 products location

    Return: list of full path S2 `.jp2` bands sorted by decreasing wavelength
    """
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
    """Search for the full path location of S2 B05, B11 and B12 bands at 10m resolution by default.
    Equivalent whether using ENS or local downloaded products within users own workspace.

    Parameters:
        item (str): full path to S2 products location

    Return: list of full path S2 `.jp2` bands sorted by decreasing wavelength
    """
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
    """Search for target MSIL2A bands given an input resolution. This is useful for index computations.

    Parameters:
        item (str): full path to S2 products location
        res (str): resolution of S2 images; default set to `10m`; allowed options: `10m`,`20m`,`60m`

    Return: bands sorted by increasing wavelength (list)
    """
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
    """Automatically search for MSIL2A bands aimed at NDWI index computation.

    Parameters:
        item (str): full path to S2 products location

    Return: S2 bands sorted by increasing wavelength (list)
    """
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
    """Compute an affine coordinates reprojection using rasterio python package, given an EPSG init argument

    Parameters:
        b (str): full path to a S2 `.jp2` file

    Return: longitude, latitude (numpy arrays)
    """
    # S2 bands share the same geometry
    ds = xarray.open_rasterio(b).isel(band=0)
    ra = rasterio.open(b,driver='JP2OpenJPEG')
    # affine transformation to lat and lon
    xt, yt = rasterio.warp.transform(src_crs=ra.crs, dst_crs=rasterio.crs.CRS(epsg), xs=ds.x,ys=ds.y)
    lon, lat = np.array(xt), np.array(yt)
    return lon,lat

def reproject(bands):
    """Generate a reprojected S2 data array ready for processing, concatenated along channel dimension.
    Call the function: affine to perform an affine transformation of coordinates

    Parameters:
        bands (list): input list of the full-path S2 bands of interest

    Return: Reprojected data array (xarray DataArray) stacked along channel dimension.
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
    """Generate a clip of a dataset given the input bounds.

    Parameters:
        ds (xarray DataArray): input dataset (from function: reproject)
        bounds (tuple): input vertexes of the clipping rectangle, provided in the order (lon_min,lon_max,lat_min,lat_max)
        plot (bool): flag to visualise clips in a plot

    Return: clipped dataset (xarray DataArray), figure if plot parameter set to True
    """
    xmin,xmax,ymin,ymax = bounds
    mask_lon = (ds.x >= xmin) & (ds.x <= xmax)
    mask_lat = (ds.y >= ymin) & (ds.y <= ymax)
    clip_ds = ds.where(mask_lon & mask_lat, drop=True)
    if plot == True:
        fig,ax = plt.subplots(1,1)
        clip_ds.plot.imshow('x','y',robust=True,ax=ax)
        plt.show()
    return clip_ds

def ratio(da):
    """Compute the ratio between two input datasets. Useful to compute indexes.

    Parameters:
        da (xarray DataArray): input dataset, concatenated along channel dimension (from funcions: reproject and clip)

    Return: ratio between datasets (xarray DataArray)
    """
    return (da.isel(channel=0).astype(float)-da.isel(channel=1).astype(float))/(da.isel(channel=0).astype(float)+da.isel(channel=1).astype(float))

def dates(products):
    """Utility function which extracts dates from S2 product name.

    Parameters:
        products (list): full-path to input products

    Return: datetime string (list)
    """
    if isinstance(products,list):
        dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S") for p in products]
        return [datetime.datetime.strftime(d,"%Y-%m-%d %H:%M") for d in dates]
    else:
        dates = datetime.datetime.strptime(products.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S")
        return [datetime.datetime.strftime(dates,"%Y-%m-%d %H:%M")]

# RGB true color equalised
def image(bands,ax=True,show_equal=False):
    """Alternative to affine reprojection and lighter in terms of RAM utilisation.
    Open raster datasets and visualise a single S2 tile on screen, adjusting color scale using Pyton open-cv equalisation.
    The extracted feature shapes are dumped into a temporary file storing coordinates vertexes, named `polygon.json` by default.

    Parameters:
        bands (list): list of full path S2 `.jp2` bands sorted by decreasing wavelength (from funcion: rgb_bands)
        ax (bool): flag optionally reversing y-axis coordinates (this may happen for a few S2 tiles depending whether ascending or descending orbit)
        show_equal (bool): flag to enable showing the equalisation histogram

    Return: equalised dataset (numpy array) stacked along channel dimension.
    """
    import rasterio.features
    from tqdm import tqdm_notebook
    import cv2
    if not bands:
        print("Error: no bands found")
        return None
    if len(bands)>3:
        bands = bands[0:-1]
    S2_files = sorted(bands)
    tmp = str(S2_files[0]).split("/")[-1].split("_")
    temp_date = datetime.datetime.strptime(tmp[1],"%Y%m%dT%H%M%S")
    title = str(datetime.datetime.strftime(temp_date,"%Y-%m-%d %H:%M"))
    # processing
    S2_images = []
    with tqdm_notebook(total=len(S2_files),desc="Opening raster data") as pbar:
        for i in S2_files:
            try:
                img = rasterio.open(i)
                img2 = img.read()
                S2_images.append(img2)
                pbar.update(1)
            except:
                raise Exception("Error occurred when reading file %s"%i)
                return 1
    # tile coordinates section
    with img as dataset:
        mask = dataset.dataset_mask()
        # Extract feature shapes and values from the array.
        for geom, val in rasterio.features.shapes(
                mask, transform=dataset.transform):
            # Transform shapes from the dataset's own coordinate
            # reference system to CRS84 (EPSG:4326).
            geom = rasterio.warp.transform_geom(dataset.crs, 'EPSG:4326', geom, precision=6)
            dump_coordinates(geom) # save
    # read coordinates to be assigned to the imshow extent
    coords = list(bounds())
    extent = tuple([coords[0],coords[2],coords[1],coords[3]])
    if ax == False:
        extent = tuple([coords[0],coords[2],coords[3],coords[1]]) # some S2 products are packed with latitude mirrored
    print("True color equalized RGB stack")
    Stk_images = np.concatenate(S2_images, axis=0)
    rgb = np.dstack((Stk_images[2],Stk_images[1],Stk_images[0]))
    norm_img = np.uint8(cv2.normalize(rgb, None, 0, 255, cv2.NORM_MINMAX))
    eq_R = cv2.equalizeHist(norm_img[:,:,0].astype(np.uint8))
    eq_G = cv2.equalizeHist(norm_img[:,:,1].astype(np.uint8))
    eq_B = cv2.equalizeHist(norm_img[:,:,2].astype(np.uint8))
    eq_RGB = np.dstack((eq_R,eq_G,eq_B))
    if show_equal == True:
        print("Equalization results")
        plt.figure(); plt.hist(norm_img[:,:,0].ravel(),bins=256,color="Blue"); plt.grid(color="lavender",lw=0.5); plt.show()
        plt.figure(); plt.hist(eq_RGB.ravel(),bins=256,color="Red");plt.grid(color="lavender",lw=0.5); plt.show()
    plt.clf();
    plt.figure(dpi=100); plt.title(title);
    plt.imshow(eq_RGB,extent=extent);
    plt.show();
    plt.close();
    return eq_RGB

def dump_coordinates(geo_json):
    """Dump coordinates into the temporary file named `polygon.json` and placed in the current working by default, collecting S2 tiles raster geometry.

    Parameters:
        geo_json (dict): S2 tile geometry features

    Return: None
    """
    import json
    filename = "polygon.json"
    file = os.path.join(os.getcwd(),filename)
    with open(file, 'w') as fp:
        json.dump(geo_json, fp)
#         print("Dump coordinates as %s"%filename)

def bounds():
    """Read coordinates from the temporary file named `polygon.json` and placed in the current working by default, collecting S2 tiles raster geometry

    Return: S2 tile vertex coordinates (tuple)
    """
    import json
    try:
        with open('polygon.json', 'r') as fp:
            polysel = json.load(fp)
            return tuple([polysel["coordinates"][0][0][0],polysel["coordinates"][0][0][1],polysel["coordinates"][0][2][0],polysel["coordinates"][0][1][1]])
    except:
        return None

def equalize_img(da):
    """Color equalization given a data array, using `cv2` Python module.
    
    Parameters:
        da (xarray.DataArray): input data array
        
    Return: color-equalized input data (xarray.DataArray)
    """
    
    import cv2, xarray
    import numpy as np
    import matplotlib.pyplot as plt

    norm_img = np.uint8(cv2.normalize(da.data, None, 0, 255, cv2.NORM_MINMAX))
    eq_R = cv2.equalizeHist(norm_img[0,:,:].astype(np.uint8))
    eq_G = cv2.equalizeHist(norm_img[1,:,:].astype(np.uint8))
    eq_B = cv2.equalizeHist(norm_img[2,:,:].astype(np.uint8))
    eq_RGB = np.dstack((eq_R,eq_G,eq_B))
    return xarray.DataArray(eq_RGB)    
