# -*- coding: utf-8 -*-
"""
 * Data and Information access services (DIAS) ONDA - For Space data distribution. 
 *
 * This file is part of CLEOPE (Cloud Earth Observation Processing Environment) software sources.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 
@author: GCIPOLLETTA

Main module aimed at data handling and visualisation of S3 product types:
    - S3 SLSTR L1 RBT
    - S3 SLSTR L2 LST
"""
import os, glob, xarray,json
import numpy as np
import seaborn as sns
sns.set(style="whitegrid", palette="pastel", color_codes=True)
import matplotlib, time
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook

def product(file):
    """Read an input product list returning a list of products suitable for reading.

    Parameters:
        file (str): full path of the input file listing target products

    Return: lines of file read (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]

def open_files(file):
    """Search for geo-coordinate file and variable file. Band S9_BT_in is chosen by default in this tutorial.
    Call funcion: product to read the input product list

    Parameters:
        file (str): full path of the input file listing target products

    Return: geo-coordinates full-path to files (str), bands full-path to files (str)
    """
    products = product(file)
    geos, bands = [],[]
    for p in products:
        geos.append(glob.glob(p+"/**/geodetic_in.nc",recursive=True)[0])
        bands.append(glob.glob(p+"/**/S9_BT_in.nc",recursive=True)[0])
    return geos,bands # coordinates and values

def datasets(geos,bands):
    """Open datasets and extract coordinates, data and attributes.

    Parameters:
        geos (list): full-path to geo-coordinates files
        bands (list): full-path to band files; default set to S9_BT_in

    Return: longitude (list),latitude (list),variable (list),sensing start attribute (list)
    Raise Exception if NetCDF HDF error is encountered (possible if using ENS)
    """
    lon, lat, var, titles = [],[],[], []
    for g,b in zip(geos,bands):
        try:
            lat.append(xarray.open_dataset(g).latitude_in)
            lon.append(xarray.open_dataset(g).longitude_in)
        except:
            raise Exception("NetCDF error when reading file %s"%g)
            continue
        try:
            var.append(xarray.open_dataset(b).S9_BT_in)
            titles.append(xarray.open_dataset(b).attrs["start_time"])
        except:
            raise Exception("NetCDF error when reading file %s"%b)
            continue
    return lon,lat,var,titles

def distribution(coords,datasets,plot=False):
    """Filter an input dataset given the clipping coordinates.

    Parameters:
        coords (tuple): input vertexes of the clipping rectangle, provided in the order: lower left corner,upper right corner (lon_min,lat_min,lon_max,lat_max)
        datasets (lists): dataset main information to be clipped: longitude,latitude,variable,sensing start attribute (from function: datasets)
        plot (bool): optional band values visualisation (temperature)

    Return: dataset filtered on coordinates (list of numpy array)
    """
    M = []
    i = 0
    xmin,ymin,xmax,ymax = coords
    lon,lat,var,titles = datasets
    for x,y in zip(lon,lat):
        rows, cols = np.where(np.logical_and(np.logical_and(y>ymin,y<ymax),np.logical_and(x>xmin,x<xmax))) # filter
        if len(rows)>0 and len(cols)>0:
            tmp_M = np.column_stack((x[rows,cols].data.ravel(),y[rows,cols].data.ravel(),var[i][rows,cols].data.ravel()))
            M.append(tmp_M)
        else:
            print("impossible to filter data %d, skipping"%i)
            titles.pop(i)
            continue
        i+=1
    if plot == True:
        fig,ax = plt.subplots(1,1,figsize=(8,4))
        for i in range(len(M)):
            sns.distplot(M[i][:,2],ax=ax,label=titles[i])
        ax.set(xlabel='  '.join([var[0].attrs["standard_name"],var[0].attrs["units"]]),title="TOA temperature distribution")
        ax.legend()
    return M

def interp_map(ds,coords,method="cubic"):
    """Interpolate a dataset using an interpolation method (cubic spline by default).

    Parameters:
        ds (lists): dataset main information to be clipped: longitude,latitude,variable,sensing start attribute (from function: datasets)
        coords (tuple): input vertexes of the clipping rectangle, provided in the order: lower left corner,upper right corner (lon_min,lat_min,lon_max,lat_max)
        method (str): interpolation method; default set to `cubic`, options: `linear`,`nearest`,`cubic`

    Return: interpolated maps (list of numpy array) in the following order: x_grid,y_grid,z_grid
    """
    xmin,ymin,xmax,ymax = coords
    gridx = np.linspace(xmin,xmax,1000)
    gridy = np.linspace(ymin,ymax,1000)
    grid_x, grid_y = np.meshgrid(gridx,gridy)
    interp_grid = []
    with tqdm_notebook(total=len(ds),desc="Data interpolation") as pbar:
        for M in ds:
            try:
                temp = griddata(M[:,0:2], M[:,-1], (grid_x, grid_y), method=method)
                interp_grid.append(temp)
            except:
                temp = griddata(M.values[:,0:2], M.values[:,-1], (grid_x, grid_y), method=method)
                interp_grid.append(temp)
            pbar.update(1)
    return grid_x, grid_y, interp_grid

def plot_map(grid_x,grid_y,mask,df,ds,centre=None):
    """Visualise interpolated datasets and the mask in the upper left corner. Be careful that this function generates plots which aspect is suited for the case study under analysis.

    Parameters:
        grid_x (numpy array): meshgrid of longitude coordinates (from funcion: interp_map)
        grid_y (numpy array): meshgrid of latitude coordinates (from funcion: interp_map)
        mask (numpy array): clipped interpolated map of masked images (from funcion: apply_diff)
        df (list of numpy arrays): interpolated maps dataset given in the following order: x_grid,y_grid,z_grid (from funcion: interp_map)
        centre (tuple): coordinates of the circle centre delimiting an area (i.e. Chernobyl exclusion zone in this tutorial); default set to None

    Return: None
    """
    lon,lat,var,titles = ds
    mins = [d[~np.isnan(d)].min() for d in df]
    maxs = [d[~np.isnan(d)].max() for d in df]
    min,max=(np.array(mins).min(),np.array(maxs).max())
    bounds = np.linspace(min, max, 256)
    norm = matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=256)
    xc,yc = centre
    circ = plt.Circle((xc, yc), 0.381,color="Red",fill=False)
    xshape,yshape = shapefile("EMSR435_AOI01_FEP_PRODUCT_observedEventA_r1_v2.json")
    n = len(titles)+1 # we add mask
    if n%2==0:
        fig, axs = plt.subplots(int(n//2),2,figsize=(10,8))
        axes = axs.ravel()
        im=axes[0].pcolormesh(grid_x,grid_y,mask,cmap="inferno")
        axes[0].set_aspect('equal', 'box')
        axes[0].plot(xc,yc,"*",color='k',markersize=10)
        axes[0].add_artist(circ)
        axes[0].plot(xshape,yshape,lw=1.,color="lime")
        axes[0].set(xlabel='longitude',ylabel='latitude')
        axes[0].set_title("mask",fontsize=8)
        divider = make_axes_locatable(axes[0])
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(im, cax=cax, orientation='vertical',label="K")
        for i,ax in enumerate(axes[1:]):
            circ = plt.Circle((xc, yc), 0.381,color="Red",fill=False)
#             im=ax.imshow(np.flip(values[i], 1),cmap="viridis",extent=extent,norm=norm,aspect="equal")
            im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="viridis")
            ax.plot(xshape,yshape,lw=1.,color="lime")
            ax.add_artist(circ)
            ax.set_aspect('equal', 'box')
            ax.plot(xc,yc,"*",color='k',markersize=10)
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[i],fontsize=8)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label="K")
        fig.tight_layout(pad=0.3)
    else:
        fig, axs = plt.subplots(int(n//2)+1,2,figsize=(10,8))
        axes = axs.ravel()
        im=axes[0].pcolormesh(grid_x,grid_y,mask,cmap="inferno")
        axes[0].set_aspect('equal', 'box')
        axes[0].plot(xc,yc,"*",color='k',markersize=10)
        axes[0].plot(xshape,yshape,lw=1.,color="lime")
        axes[0].add_artist(circ)
        axes[0].set(xlabel='longitude',ylabel='latitude')
        axes[0].set_title("mask",fontsize=8)
        divider = make_axes_locatable(axes[0])
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(im, cax=cax, orientation='vertical',label="K")
        for i,ax in enumerate(axes[1:-1]):
            circ = plt.Circle((xc, yc), 0.381,color="Red",fill=False)
            im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="viridis")
            ax.set_aspect('equal', 'box')
#             im=ax.imshow(values[i],cmap="viridis",extent=extent,norm=norm,aspect="equal")
            ax.plot(xc,yc,"*",color='k',markersize=10)
            ax.add_artist(circ)
            ax.plot(xshape,yshape,lw=1.,color="lime")
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[i],fontsize=8)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label="K")
        axes[-1].axis('off')
        fig.tight_layout(pad=0.3)
    return

def apply_diff(x,y,target_df,coords,file="slstr_mask.txt",plot=False):
    """Produce a mask from sample images sensed at specific dates, clipping the original data on given coordinates, interpolating using a cubic spline
    and taking the median of these values.
    Returns the mask array and the difference map between target data and mask.

    Parameters:
        x (numpy array): meshgrid of longitude coordinates (from funcion: interp_map)
        y (numpy array): meshgrid of latitude coordinates (from funcion: interp_map)
        target_df (list of numpy arrays): interpolated maps dataset given in the following order: x_grid,y_grid,z_grid (from funcion: interp_map)
        coords (tuple): input vertexes of the clipping rectangle, provided in the order: lower left corner,upper right corner (lon_min,lat_min,lon_max,lat_max)
        file (str): full path of the input file listing target products, mask images in this tutorial
        plot (bool): optional band values visualisation (temperature) of the mask dataset

    Return: median values map of interpolated mask images (numpy array), difference map (numpy array)
    """
    sample_df = reference_df(file,coords) # sample images days before the event
    interp_grid = []
    with tqdm_notebook(total=len(sample_df),desc="Mask interpolation") as pbar:
        for data in sample_df:
            temp = griddata(data[:,0:2], data[:,-1], (x, y), method="cubic")
            interp_grid.append(temp)
            pbar.update(1)
    stacked_mask = np.dstack((interp_grid))
    mask = np.median(stacked_mask,axis=2) # pixel along deep axis <<<
#     plt.pcolormesh(x,y,mask);plt.colorbar();plt.title("mask")
    diff = [np.subtract(d,mask) for i,d in enumerate(target_df)]
    if plot==True:
        # plot out mask
        fig,ax = plt.subplots(1,1)
        sns.distplot(mask.ravel(),ax=ax,label="mask",hist=True)
        ax.set(xlabel="T (K)")
        ax.legend()
    return mask,diff

def reference_df(file,coords):
    """Generate a clip of a dataset, given the input file and coordinates.

    Parameters:
        file (str): full path of the input file listing target products to be clipped
        coords (tuple): input vertexes of the clipping rectangle, provided in the order: lower left corner,upper right corner (lon_min,lat_min,lon_max,lat_max)

    Return: dataset filtered on coordinates (list of numpy array)
    """
    geometry,bands = open_files(file)
    ds = datasets(geometry,bands)
    return distribution(coords,ds,plot=False)

def uncertainity(file):
    """Compute the radiometric uncertainty of S9_BT_in values.

    Parameters:
        file (str): full path of the input file listing target products

    Return: mean radiometric uncertainty values (list)
    """
    products = product(file)
    unc = []
    for p in products:
        unc.append(glob.glob(p+"/**/S9_qual*in.nc",recursive=True)[0])
    if len(unc)>1:
        ds = [xarray.open_dataset(f).S9_radiometric_uncertainty_in.data for f in unc]
        a = [dataset.mean() for dataset in ds]
    return a

def shapefile(file):
    """Open and load a given input file.

    Parameters:
        file (str): full path of the input file listing target products to be clipped

    Return: longitude,latitude (tuple) of the shapefile
    """
    with open(file) as json_file:
        data = json.load(json_file)
    aline = np.array(data["features"][2]["geometry"]["coordinates"][0])
    return aline[:,0],aline[:,1] #lon,lat

def draw_circle(centre,radius=0.381):
    """Define a circular shape given radius and centre coordinates.

    Parameters:
        centre (tuple): centre circle coordinates
        radius (float): circle radius; default set to 0.381 (i.e. Chernobyl exclusion radius)

    Return: longitude,latitude (tuple) coordinates of the circle.
    """
    xc,yc = centre
    angles = np.linspace(0, 2*np.pi, 100)
    return (radius*np.sin(angles)+xc,radius*np.cos(angles)+yc)

# plot the map after interpolation (no mask)
def image(grid_x,grid_y,df,ds,centre=None):
    """Visualise interpolated datasets. Be careful that this function generates plots which aspect is suited for the case study under analysis.
    Parameters:
        grid_x (numpy array): meshgrid of longitude coordinates (from funcion: interp_map)
        grid_y (numpy array): meshgrid of latitude coordinates (from funcion: interp_map)
        df (list of numpy arrays): interpolated maps dataset given in the following order: x_grid,y_grid,z_grid (from funcion: interp_map)
        ds (list of numpy arrays): longitude,latitude,variable,sensing start attribute (from funcion: datasets)
        centre (tuple): coordinates of the circle centre delimiting an area (i.e. Chernobyl exclusion zone in this tutorial); default set to None

    Return: matplotlib figure
    """
    lon,lat,var,titles = ds
    mins = [d[~np.isnan(d)].min() for d in df]
    maxs = [d[~np.isnan(d)].max() for d in df]
    min,max=(np.array(mins).min(),np.array(maxs).max())
    bounds = np.linspace(min, max, 256)
    norm = matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=256)
    xc,yc = centre
    n = len(titles) # we add mask
    if n%2==0:
        fig, axs = plt.subplots(int(n//2),2,figsize=(10,8))
        axes = axs.ravel()
        for i,ax in enumerate(axes[1:]):
            im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="magma")
            ax.set_aspect('equal', 'box')
            ax.plot(xc,yc,"o",color='k',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[i],fontsize=8)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label="K")
        fig.tight_layout(pad=0.3)
    else:
        if n==1:
            fig,ax = plt.subplots(1,1,figsize=(10,8),dpi=100)
            im = ax.pcolormesh(grid_x,grid_y,df[0],norm=norm,cmap="magma")
            ax.set_aspect('equal', 'box')
            ax.plot(xc,yc,"o",color='k',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
            ax.set(xlabel='longitude',ylabel='latitude')
            ax.set_title(titles[0],fontsize=12)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical',label="K")
            fig.tight_layout()
        else:
            fig, axs = plt.subplots(int(n//2)+1,2,figsize=(10,8))
            axes = axs.ravel()
            for i,ax in enumerate(axes[:-1]):
                im = ax.pcolormesh(grid_x,grid_y,df[i],norm=norm,cmap="magma")
                ax.set_aspect('equal', 'box')
                ax.plot(xc,yc,"o",color='k',markersize=10,markerfacecolor="None",markeredgecolor='lime', markeredgewidth=1.)
                ax.set(xlabel='longitude',ylabel='latitude')
                ax.set_title(titles[i],fontsize=8)
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)
                fig.colorbar(im, cax=cax, orientation='vertical',label="K")
            axes[-1].axis('off')
            fig.tight_layout(pad=0.3)
    return fig

def LST_dataset(products):
    """ Open S3 SLSTR L2 LST products as xarray datasets and merge variables and coordinates in a single dataset, using `join=exact` option into xarray.merge
    
    Parameters:
        - products (list): list of input S3 products, read from file or given explicitly
    
    Return: merged LST datasets (list of xarray dataset)
    Raise Exception if NetCDF HDF error is encountered (possible if using ENS)
    """
    geodetic, lst_in = [],[]
    for p in products:
        fg = glob.glob(p+"/**/geodetic_in.nc",recursive=True)[0]
        fl = glob.glob(p+"/**/LST_in.nc",recursive=True)[0]
        try:
            geodetic.append(xarray.open_dataset(fg))
            lst_in.append(xarray.open_dataset(fl))
        except:
            raise Exception("NetCDF error when reading product: %s"%p)
    datasets = []
    for geo,var in zip(geodetic,lst_in):
        merge_ds = xarray.merge([geo,var],join="exact")
        da = merge_ds.assign_coords(lon=merge_ds.longitude_in,lat=merge_ds.latitude_in).LST
        da.attrs["time"] = geo.attrs["start_time"]
        datasets.append(da)
    del merge_ds,da
    if len(datasets)>1:
        return datasets
    else:
        return datasets[0]
        