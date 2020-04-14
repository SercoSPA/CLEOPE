import xarray, glob, os, subprocess, time
import pandas as pd

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

def wrap(coords,file):
    xmin,ymin,xmax,ymax = coords # tuple containing coordinates to clip
    make_dir() # create directory where to dump clipped files
    localpath = os.path.join(os.getcwd(),"clipped_files")
    cmd_file = "clipper.sh" # filename bash 
    for inputfile in file:
        command = ""
        outputfile = os.path.join(localpath,inputfile.split("/")[-1].split(".")[0]+"_clip.tiff")    
        command = "gdalwarp -te %s %s %s %s %s %s \n" % (xmin, ymin, xmax, ymax, inputfile, outputfile)
        print(command)
        print("Wrapping image: %s"%inputfile.split("/")[-1].split(".")[0])
        with open(os.path.join(cmd_file), 'w') as f:
            f.write(command)
            f.close()    
        # run bash file
        run(cmd_file)
        time.sleep(10) # sleep 30 seconds before proceeding
    print("Resampled data sets in: %s"%localpath)
    
    
def run(file):
    try:
        cmd = subprocess.Popen(['bash', str(file)])
    except:
        raise Exception("Error when running file %s"%file)

def image():
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
        g_simple = t.plot(x='x', y='y',col='UTC',col_wrap=2,robust=True,cmap="binary_r",figsize=(15,6))
        return data_sets
    else:
        print("No .tiff clips found in clipped_files folder")
        return None
        