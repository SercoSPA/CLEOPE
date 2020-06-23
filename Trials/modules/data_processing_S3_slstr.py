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
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]
    
def open_files(file):
    products = product(file)
    geos, bands = [],[]
    for p in products:
        geos.append(glob.glob(p+"/**/geodetic_in.nc",recursive=True)[0])
        bands.append(glob.glob(p+"/**/S9_BT_in.nc",recursive=True)[0])
    return geos,bands # coordinates and values
    
def datasets(geos,bands):        
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
    geometry,bands = open_files(file)
    ds = datasets(geometry,bands)
    return distribution(coords,ds,plot=False)

def uncertainity(file):
    products = product(file)
    unc = []
    for p in products:
        unc.append(glob.glob(p+"/**/S9_qual*in.nc",recursive=True)[0])
    if len(unc)>1:
        ds = [xarray.open_dataset(f).S9_radiometric_uncertainty_in.data for f in unc]
        a = [dataset.mean() for dataset in ds]
    return a

def shapefile(file):
    with open(file) as json_file:
        data = json.load(json_file)
    aline = np.array(data["features"][2]["geometry"]["coordinates"][0])
    return aline[:,0],aline[:,1] #lon,lat

def draw_circle(centre,radius=0.381):
    xc,yc = centre
    angles = np.linspace(0, 2*np.pi, 100)
    return (radius*np.sin(angles)+xc,radius*np.cos(angles)+yc)

# plot the map after interpolation (no mask)
def image(grid_x,grid_y,df,ds,centre=None):
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