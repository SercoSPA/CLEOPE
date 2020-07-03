# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com

Main module aimed at S5P L2 data handling and visualisation.
"""
import os, glob,json, datetime,xarray
from netCDF4 import Dataset
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata
from pathlib import Path
import warnings

cmap = matplotlib.cm.magma_r

from holoviews import opts
import holoviews as hv
hv.extension('matplotlib')

L2_variables = {"CO":"carbonmonoxide_total_column",
                "HCHO":"formaldehyde_tropospheric_vertical_column",
                "CH4":"methane_mixing_ratio",
                "SO2":"sulfurdioxide_total_vertical_column",
                "NO2":"nitrogendioxide_tropospheric_column",
                "O3":"ozone_total_vertical_column",
               }

def query(file):
    """Read an input product list returning the full-path product list suitable for reading datasets.

    Parameters:
        file (str): full-path of the input file listing target products

    Return: S5P L2 full-path to files (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    products = []
    for item in list:
        if item.endswith('.nc'):
            products.append(item)
        else:
            for file in Path(item).rglob('*.nc'):
                products.append(str(file))
    return products

def read_coordinates(path=os.getcwd(),filename='polygon.json'):
    """Read coordinates from a shapefile (i.e. generated into SEARCH notebook).

    Parameters:
        path (str): full-path of the shapefile location; default set to the current working directory
        filename (str): name of the input shapefile file; default set to `polygon.json`

    Return: shapefile boundary vertexes (list) in the order: lat_min,lat_max,lon_min,lon_max
    """
    file = glob.glob(os.path.join(path,filename),recursive=True)[0]
    with open(file, 'r') as fp:
        polysel = json.load(fp)
    if polysel["type"] == "Polygon":
        bounds = polysel["coordinates"][0]
    elif polysel["type"] == "LineString":
        bounds = polysel["coordinates"]
    bounds_stack = np.column_stack(bounds)
    return [bounds_stack[1].min(),bounds_stack[1].max(),bounds_stack[0].min(),bounds_stack[0].max()]

def read(bounds,file):
    """Open and read datasets from a given product list, clipping over input coordinates.

    Parameters:
        bounds (tuple): input vertexes of the clipping rectangle, provided in the order: (lat_min,lat_max,lon_min,lon_max)
        file (str): full-path of the input file listing target products

    Return: clipped datasets (list)
    Raise Exception if NetCDF HDF error is encountered (possible if using ENS)
    """
    products = query(file)
    latmin,latmax,lonmin,lonmax = bounds
    datasets = list()
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
                print("Key Error: unknown variable")
                return 1
            b = np.ma.where(np.logical_and(np.logical_and(lat>=latmin,lat<=latmax),np.logical_and(lon>lonmin,lon<lonmax)))
            A = np.ma.zeros((len(b[0]),3))
            A[:,1] = lat[b]  #y
            A[:,0] = lon[b]  #x
            A[:,2] = var[b]  #z
            dataframe = pd.DataFrame(data=A,columns=["lon","lat",key])
            datasets.append(dataframe)
        except:
            raise Exception("NetCDF Error occurred when reading file: %s"%file)
            continue
    return datasets # all datasets related to product file list

def dates(products):
    """Utility function which extracts dates from S5P L2 product name.

    Parameters:
        products (list): S5P L2 full-path to files (from function: query)

    Return: datetime string (list)
    """
    dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[-6],"%Y%m%dT%H%M%S") for p in products]
    return [datetime.datetime.strftime(d,"%Y - %b - %d") for d in dates]

def units(file):
    """Utility function which extracts units from S5P L2 product name.

    Parameters:
        file (str): full-path of the input file listing target products

    Return: dataset units (str) per each product
    """
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
    """Compute and plot mean values of an input dataset over time. This is useful to generate a timeseries monitoring of the same area in the variable of interest.

    Parameters:
        df (list): clipped input dataframes (from funcion: read)
        key (str): name of S5P L2 variable to monitor
        file (str): full-path of the input file listing target products

    Return: mean values dataframe (pandas dataframe)
    """
    if key not in list(L2_variables.keys()):
        raise KeyError("Unknown key, call dp.L2_variables.keys() to display choices.")
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
    xlims=(data.iloc[0,0],data.iloc[-1,0])
    fig,ax = plt.subplots(1,1,constrained_layout=False)
    if key == "NO2":
        variable = data.val_u*1E6
        ax.plot(data.date,variable,"-o")
        label = str(key)+" u"+str(u)
        ylims = (variable.min()-variable.min()*0.1,variable.max()+variable.max()*0.1)
    else:
        variable = data.val_u*1E3
        ax.plot(data.date,variable,"-o")
        label = str(key)+" m"+str(u)
        ylims = (variable.min()-variable.min()*0.1,variable.max()+variable.max()*0.1)
    ax.set(xlim=xlims,ylim=ylims,xlabel="date",ylabel=label,title="Timeseries of %s mean value over selected area"%key)
    ax.grid(color="lavender")
    ax.set_xticks(days)
    fig.autofmt_xdate()
    return data

def mapping(bounds,ds,file,plotmap=False,centre=(None,None),dynamic=False,method='cubic'):
    """Generate and plot an interpolated map given an input clipped dataset, using by default a cubic spline.
    Colors are automatically normalised on the maximum value to facilitate comparisons.

    Parameters:
        bounds (tuple): input vertexes of the clipping rectangle, provided in the order: (lat_min,lat_max,lon_min,lon_max)
        ds (list): clipped datasets (from funcion: read)
        file (str): full-path of the input file listing target products
        plotmap (bool): optionally plot the interpolated maps; default set to False
        centre (tuple): centre coordinates to draw a circle delimitating an area; default set to None
        dynamic (bool): enable a dynamic colorbar; default set to False (to facilitate comparisons)
        method (str): interpolation method; default set to `cubic`, options: `linear`,`nearest`,`cubic`

    Return: interpolated map grid in the form: grid_x,grid_y,grid_z (numpy arrays), matplotlib figure (if plot is enabled)
    """
    ymin,ymax,xmin,xmax = bounds
    gridx = np.linspace(xmin,xmax,1000)
    gridy = np.linspace(ymin,ymax,1000)
    grid_x, grid_y = np.meshgrid(gridx,gridy)
    maps = []
    for dataset in ds:
        M = np.copy(dataset.values)
        interp = griddata(M[:,0:2], M[:,-1], (grid_x, grid_y), method=method)
        maps.append(interp*1E3)
    if plotmap==True:
        keys = [d.columns[-1] for d in ds]
        fig = plot_maps(grid_x, grid_y, maps, file, centre, keys, dynamic)
    else:
        fig = None
    return grid_x,grid_y,maps,fig

def plot_maps(grid_x, grid_y, df, file, centre, keys, dynamic=False):
    """Plot a map given the input meshgrids. Colors are automatically normalised on the maximum value to facilitate comparisons.

    Parameters:
        grid_x (numpy array): meshgrid of longitude coordinates (from funcion: mapping)
        grid_y (numpy array): meshgrid of latitude coordinates (from funcion: mapping)
        df (list): clipped datasets (from funcion: read)
        file (str): full-path of the input file listing target products
        centre (tuple): centre coordinates to draw a circle delimitating an area
        keys (str): names of S5P L2 variable to monitor
        dynamic (bool): enable a dynamic colorbar; default set to False (to facilitate comparisons)

    Return: matplotlib figure
    """
    xc,yc = centre
    if dynamic==True:
        maxs = [d[~np.isnan(d)].max() for d in df]
        bounds = [np.linspace(0, max, 256) for max in maxs]
        norm = [matplotlib.colors.BoundaryNorm(boundaries=b, ncolors=256) for b in bounds]
    else:
        maxs = [d[~np.isnan(d)].max() for d in df]
        min,max=(0,np.array(maxs).max())
        bounds = np.linspace(0, max, 256)
        norm = matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=256)
    products = query(file)
    titles = [xarray.open_dataset(p).attrs["time_coverage_start"] for p in products]
    unit = units(file)
    n = len(df)
    if n%2==0:
        fig, axs = plt.subplots(int(n//2),2,figsize=(12,10),dpi=75)
        axes = axs.ravel()
        for i,ax in enumerate(axes):
            if dynamic==True:
                im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm[i],cmap="magma")
            else:
                im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="magma")
            ax.plot(xc,yc,'o',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
            ax.set_aspect('equal', 'box')
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[i],fontsize=12)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label=keys[i]+" m"+unit)
        fig.tight_layout()
    else:
        if n==1:
            i=0
            fig, ax = plt.subplots(1,1,figsize=(8,6),dpi=100)
            if dynamic==True:
                im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm[i],cmap="magma")
            else:
                im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="magma")
            ax.plot(xc,yc,'o',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
            ax.set_aspect('equal', 'box')
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[i],fontsize=12)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label=keys[i]+" m"+unit)
            fig.tight_layout()
        else:
            fig, axs = plt.subplots(int(n//2)+1,2,figsize=(10,8))
            axes = axs.ravel()
            for i,ax in enumerate(axes[:-1]):
                if dynamic==True:
                    im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm[i],cmap="magma")
                else:
                    im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="magma")
                ax.plot(xc,yc,'o',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
                ax.set_aspect('equal', 'box')
                ax.set(xlabel='longitude',ylabel='latitude')
                ax.set_title(titles[i],fontsize=12)
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)
                fig.colorbar(im, cax=cax, orientation='vertical',label=keys[i]+" m"+unit)
            axes[-1].axis('off')
            fig.tight_layout()
    return fig

def read_dataset(files,key,qa_val=0.0,bounds=None):
    """Open and read data from `.nc` files, clipping the dataset on a given rectangle.

    Parameters:
        files (list): S5P L2 full-path to files (from function: query)
        key (str): name of S5P L2 variable to monitor
        qa_val (float): quality threshold to filter a S5P L2 data array
        bounds (tuple): input vertexes of the clipping rectangle, provided in the order: (lon_min,lon_max,lat_min,lat_max); default set to None

    Return: clipped subsets (list of xarray DataArray)
    """
    if key not in list(L2_variables.keys()):
        warnings.warn("Unknown key, call dp.L2_variables.keys() to display choices.")
        return
    else:
        var = L2_variables[str(key)]
    try:
        darray = [xarray.open_dataset(f,group="PRODUCT").isel(time=0) for f in files]
    except:
        raise Exception("Exception occurred when handling input files")
    subsets = []
    for data in darray:
        # clip dataset
        if bounds!=None:
            xmin,xmax,ymin,ymax=bounds
            da_sel = data.where(((data.longitude<xmax) & (data.longitude>xmin) & (data.latitude<ymax) & (data.latitude>ymin)), drop=True)
        else:
            da_sel = data.copy()
        # quality
        da = da_sel.where(da_sel["qa_value"]>qa_val,drop=True)
        # convert dataset
        da_conv = (da[var].multiplication_factor_to_convert_to_molecules_percm2*da[var])
        da_conv.attrs["time"] = np.datetime_as_string(data.time.data)
        subsets.append(da_conv)
        del da,da_sel
    return subsets

def mosaic(da_list,dims=["ground_pixel","scanline"]):
    """Convert S5P xarray DataArray into datasets and create a mosaic using native dimensions (i.e. scanline and ground_pixel). The `combine_nested` xarray function is used to achieve this result.
    
    Parameters:
        da_list (list of xarray DataArray): S5P input list of (clipped) dataset to be mosaicked (as read by `read_dataset` function)
        dims (list of str): dimensions along which to concatenate variables. Set `concat_dim=[..., None, ...]` explicitly to disable concatenation and merge instead along a particular dimension. The position of None in the list specifies the dimension of the nested-list input along which to merge. Must be the same length as the depth of the list passed to datasets.
        
    Return: `xarray.combine_nested` result (xarray dataset)
    """
    ds_5p = [[sub.to_dataset()] for sub in da_list]
    return xarray.combine_nested(ds_5p,concat_dim=dims)
    