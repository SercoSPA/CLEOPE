import xarray, glob, os, subprocess, time
import pandas as pd
import warnings
import matplotlib.pyplot as plt

def make_dir():
    try:
        os.makedirs('clipped_files')
    except:
        return None

def product(file):
    with open(file,"r") as f:
        data = f.readlines()
        return [d.split("\n")[0] for d in data]

def open_band(products, pol="vh"):
    file = []
    for p in products:
        for f in glob.glob(p+"/**/*vh*.tiff",recursive=True):
            file.append(f)
    return file

def wrap(coords,products):
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
        time.sleep(30) # sleep 30 seconds before proceeding
    print("Resampled data sets in: %s"%localpath)
    
    
def run(file):
    try:
        cmd = subprocess.Popen(['bash', str(file)])
    except:
        raise Exception("Error when running file %s"%file)

def image(rgb=False):
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
        