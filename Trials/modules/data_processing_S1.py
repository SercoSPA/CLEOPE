# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com

Main module aimed at S1 data handling and visualisation.
"""
import xarray, glob, os, subprocess, time
import pandas as pd
import warnings
import matplotlib.pyplot as plt

def make_dir():
    """Create a new directory named `clipped_files` if do not exists.

    Return: None
    """
    try:
        os.makedirs('clipped_files')
    except:
        return None

def product(file):
    """Read an input product list returning a list of products suitable for reading.

    Parameters:
        file (str): full path of the input file product list

    Return: lines of file read (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]

def open_band(products, pol="vh"):
    """Open S1 bands given input products, returning full-path input file list suitable for reading.

    Parameters:
        products (list): list of string of product location
        pol (str): S1 polarization option; default set to `vh`

    Return: full-path of S1 `tiff` files (list)
    """
    file = []
    for p in products:
        for f in glob.glob(p+"/**/*"+str(pol)+"*.tiff",recursive=True):
            file.append(f)
    return file

def wrap(coords,products):
    """Main funcion to create a clip of the raster datasets (via gdalwarp option from command line) given a tuple of input coordinates.
    This is useful to zoom-in a portion of the native image.
    By default a temporary file named `clipper.sh` is created containing the instructions for clipping, aimed at using GDAL Python package.
    Process runs in the background for 20 seconds per each clip.
    By default the output clips are automatically saved in the directory `/clipped_files` and named after the original product with the addition of `_clip` in the end.
    Note that equal clipped files are not overwritten.

    Parameters:
        coords (tuple): input vertexes of the clipping rectangle, provided in the order: lower left corner,upper right corner (lon_min,lat_min,lon_max,lat_max)

    Return: None
    """
    xmin,ymin,xmax,ymax = coords # tuple containing coordinates to clip
    make_dir() # create directory where to dump clipped files
    localpath = os.path.join(os.getcwd(),"clipped_files")
    cmd_file = "clipper.sh" # filename bash
    for inputfile in products:
        command = ""
        outputfile = os.path.join(localpath,inputfile.split("/")[-1].split(".")[0]+"_clip.tiff")
        command = "gdalwarp -te %s %s %s %s %s %s \n" % (xmin, ymin, xmax, ymax, inputfile, outputfile)
        print("Wrapping image: %s"%inputfile.split("/")[-1].split(".")[0])
        print(command)
        with open(os.path.join(cmd_file), 'w') as f:
            f.write(command)
            f.close()
        # run bash file
        run(cmd_file)
        time.sleep(20) # wait before proceeding
    print("Resampled data sets in: %s"%localpath)


def run(file):
    """Run a bash script subprocess in the background.

    Parameters:
        file (str): full path of the bash file to run

    Return: None
    Raise Exception if process fails.
    """
    try:
        cmd = subprocess.Popen(['bash', str(file)])
    except:
        raise Exception("Error when running file %s"%file)

def image(rgb=False):
    """Data handling and visualisation of S1 clipped datasets.
    Clips are automatically taken from clipped_files folder by default. We stronlgy recommand to clip datasets to avoid RAM overquota.
    Raster datasets are concatenated along a new dimension (time) extracted from TIFFTAG_DATETIME attribute of S1 data arrays, and then transposed to be properly sliced along the new time dimension to create stacked layers.
    Images are visualised on a normalised color scale and automatically arranged into columns.
    Optionally a colored RGB stack can be visualised too, using 3 stacked layers along `time` dimension (i.e. representing the channel).

    Parameters:
        rgb (bool): flag to enable RGB stack

    Return: handled S1 data array
    """
    clipped_files = glob.glob("clipped_files/*.tiff",recursive=True)
    if len(clipped_files)>0:
        data_sets, titles = [], []
        for f in clipped_files:
            tmp = xarray.open_rasterio(f).isel(band=0)
            data_sets.append(tmp)
            titles.append(tmp.attrs["TIFFTAG_DATETIME"])
        dc = xarray.concat([d for d in data_sets],pd.Index([d.attrs["TIFFTAG_DATETIME"] for d in data_sets]))
        dc = dc.rename({"concat_dim":"UTC"})
        t = dc.transpose("x","y","UTC").isel(UTC=slice(0,len(data_sets),1))
        if dc.shape[0]<3:
            if dc.shape[0]==1:
                col_warp = 1
            else:
                col_warp = 2
        else:
            col_warp = 3
        g_simple = t.plot(x='x', y='y',col='UTC',col_wrap=col_warp,robust=True,cmap="binary_r",figsize=(15,5),cbar_kwargs={'pad':0.02})
        RGB(dc,rgb)
        return dc
    else:
        warnings.warn("No tiff clips found in clipped_files folder")
        return None

def RGB(dc,rgb):
    """Compose an RGB stack, given a 3D data array input

    Parameters:
        dc (xarray Data Array): input datasets concatenated along time dimension
        rgb (flag): flag to enable RGB stack

    Return: None
    """
    # check dimensions along time
    if rgb == True:
        if dc.shape[0]!=3:
            warnings.warn("Invalid shape for RGB stack")
        else:
            dc["band"] = "RGB"
            dc.plot.imshow(robust=True,figsize=(8,6))
            plt.show()
    else:
        return
