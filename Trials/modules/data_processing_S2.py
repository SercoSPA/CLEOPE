import pandas as pd
import os, glob, datetime, json
import rasterio 
import rasterio.features
import numpy as np
from tqdm import tqdm_notebook
import cv2
import matplotlib.pyplot as plt
from ipywidgets import widgets, Layout
import datetime
import seaborn as sns
cmap = sns.color_palette("RdYlGn",256)
cmap1 = sns.color_palette("GnBu_d",256)
from holoviews import opts
import holoviews as hv
import numpy.ma as ma
from pathlib import Path
hv.extension('matplotlib')
sns.set_style("ticks")

def products(file):
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    if "_local" in file:
        return list 
    elif "_remote" in file:
        return list
    else:
        print("Error invalid filename.")
        return None

def _list_():
    return glob.glob("list*",recursive=True)
    
def choose_files():
    mission = widgets.Dropdown(
    options=_list_(),
    description='Product:',
    layout=Layout(width="30%"),
    disabled=False,
    )
    display(mission)
    label = widgets.Label()
    btn = widgets.Button(description="CLICK to submit")
    display(btn)
    return mission,btn,label    

def open_rgb_bands(product):
    if (product.find('MSIL2A') != -1):
        try:
            S2_files = [f for f in glob.glob(product+"/**/*[2-4]_10m.jp2",recursive=True)]
        except:
            raise Exception("Product %s not found"%product)
            return None
    elif (product.find('MSIL1C') != -1):
        try:
            S2_files = [f for f in glob.glob(product+"/**/*[2-4].jp2",recursive=True)]
        except:
            raise Exception("Product %s not found"%product)
            return None
    else:
        print("Error. Choose L1C or L2A products")
        return 1
    if S2_files:
        print("Access to files:\n")
        print("\n\n".join(sorted(S2_files))) 
        return sorted(S2_files) # sorted option interface for local files 
    else:
        print("Warning: no files found!")
        return None

def choose(mlist):
    mission = widgets.Dropdown(
    options=mlist,
    description='Product:',
    layout=Layout(width="95%"),
    disabled=False,
    )
    display(mission)
    label = widgets.Label()
    btn = widgets.Button(description="CLICK to submit")
    display(btn)
    return mission,btn,label

# plot stack of 3 colors 
def image(S2_files,ax=True,show_equal=False):
    if not S2_files:
        print("Error: no bands found")
        return None
    if len(S2_files)>3:
        print("\n !! Too many bands opened for an RGB stack !!")
        S2_files = S2_files[0:-1]
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
    with img as dataset: # ne basta una 
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
    print("- Creating RGB stack")
    Stk_images = np.concatenate(S2_images, axis=0)
    rgb = np.dstack((Stk_images[2],Stk_images[1],Stk_images[0]))
    print("- Equalizing")
    norm_img = np.uint8(cv2.normalize(rgb, None, 0, 255, cv2.NORM_MINMAX))
    eq_R = cv2.equalizeHist(norm_img[:,:,0].astype(np.uint8))
    eq_G = cv2.equalizeHist(norm_img[:,:,1].astype(np.uint8))
    eq_B = cv2.equalizeHist(norm_img[:,:,2].astype(np.uint8))
    eq_RGB = np.dstack((eq_R,eq_G,eq_B)) 
    if show_equal == True:
        print("Equalization results")
        plt.figure(); plt.hist(norm_img[:,:,0].ravel(),bins=256,color="Blue"); plt.grid(color="lavender",lw=0.5); plt.show()
        plt.figure(); plt.hist(eq_RGB.ravel(),bins=256,color="Red");plt.grid(color="lavender",lw=0.5); plt.show()
    print("- Plotting...")
    plt.clf();
    plt.figure(dpi=100); plt.title(title);
    plt.imshow(eq_RGB,extent=extent); 
    plt.show()
    plt.close()
    return eq_RGB

def nbr(products):
    if isinstance(products,list):
        files = list()
        for p in products:
            if (p.find('MSIL2A') != -1):
                try:
                    b8 = glob.glob(p+"/**/*B8A_20m.jp2",recursive=True)[0]
                    b12 = glob.glob(p+"/**/*B12_20m.jp2",recursive=True)[0]
                except:
                    raise Exception("File %s bands not found: Error occurred when opening bands"%p)
            else:
                try:
                    b8 = glob.glob(p+"/**/*B8A.jp2",recursive=True)[0]
                    b12 = glob.glob(p+"/**/*B12.jp2",recursive=True)[0]
                except:
                    raise Exception("File %s bands not found: Error occurred when opening bands"%p)
                    continue
            files.append([b8,b12])
    else:
        files = []
        if (products.find('MSIL2A') != -1):
            try:
                b8 = glob.glob(products+"/**/*B8A_20m.jp2",recursive=True)[0]
                b12 = glob.glob(products+"/**/*B12_20m.jp2",recursive=True)[0]
            except:
                raise Exception("File %s bands not found: Error occurred when opening bands"%products)
        else:
            try:
                b8 = glob.glob(products+"/**/*B8A.jp2",recursive=True)[0]
                b12 = glob.glob(products+"/**/*B12.jp2",recursive=True)[0]
            except:
                raise Exception("File %s bands not found: Error occurred when opening bands"%p)
        files.append([b8,b12])
    images = []
    with tqdm_notebook(total=len(files)*len(files[0]),desc="Opening raster data") as pbar:
        for f in files:
            temp_img = []
            for i in range(len(f)):
                try:
                    temp = (rasterio.open(f[i])).read(1)
                    temp_img.append(temp)
                    pbar.update(1)
                except:
                    raise Exception("Rasterio Error while reading file %s"%f[i])
                    return 1
            images.append(temp_img)
    nbr_series = []
    with np.errstate(divide="ignore",invalid="ignore"):
        for im in images:
            div = (im[0].astype(float)-im[1].astype(float))/(im[0]+im[1])
            nbr_series.append(div)
    return nbr_series

def dates(products):
    if isinstance(products,list):
        dates = [datetime.datetime.strptime(p.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S") for p in products]
        return [datetime.datetime.strftime(d,"%b/%d/%Y") for d in dates]
    else:
        dates = datetime.datetime.strptime(products.split("/")[-1].split("_")[2],"%Y%m%dT%H%M%S")
        return [datetime.datetime.strftime(dates,"%b/%d/%Y")]

def bounds():
    try:
        with open('polygon.json', 'r') as fp:
            polysel = json.load(fp)
            return tuple([polysel["coordinates"][0][0][0],polysel["coordinates"][0][0][1],polysel["coordinates"][0][2][0],polysel["coordinates"][0][1][1]])
    except:
        return None

def plot(nbr,label=[],bounds=None):
    if not label:
        label = ["Title" for i in range(len(nbr))]
    images = []
    i = 0
    for nbr in nbr:
        if bounds != None:
            images.append(hv.Image(nbr,bounds=bounds).opts(cmap=cmap,colorbar=True,title=label[i]))
        else:
            images.append(hv.Image(nbr).opts(cmap=cmap,colorbar=True,xaxis=None,yaxis=None,title=label[i]))
        i+=1
    return images
            
def ndsi(products):
    if isinstance(products,list):
        files = list()
        for p in products:
            if (p.find('MSIL2A') != -1):
                a = glob.glob(os.path.join(p,"**/*B03_20m.jp2"),recursive=True)[0]
                b = glob.glob(os.path.join(p,"**/*B11_20m.jp2"),recursive=True)[0]
                files.append([a,b])
            else:
                print("L1C not supported; skip")
                continue
    else:
        files = list()
        if (products.find('MSIL2A') != -1):
            a = glob.glob(os.path.join(products,"**/*B03_20m.jp2"),recursive=True)[0]
            b = glob.glob(os.path.join(products,"**/*B11_20m.jp2"),recursive=True)[0]
            files.append([a,b])
        else:
            raise Exception("L1C not supported")
            return None 
    images = []
    with tqdm_notebook(total=len(files)*len(files[0]),desc="Opening raster data") as pbar:
        for f in files:
            temp_img = []
            for i in range(len(f)):
                try:
                    temp = (rasterio.open(f[i])).read(1)
                    temp_img.append(temp)
                    pbar.update(1)
                except:
                    raise Exception("Rasterio Error while reading file %s"%f[i])
                    return 1
            images.append(temp_img)
    ratio = []
    with np.errstate(divide="ignore",invalid="ignore"):
        for im in images:
            div = (im[0].astype(float)-im[1].astype(float))/(im[0]+im[1])
            ratio.append(div)
    return ratio

def open_rgb_snow(product):
    S2_files = []
    if (product.find('MSIL2A') != -1):
        bands = ["*B12_20m.jp2","*B11_20m.jp2","*B05_20m.jp2"]
        for b in bands:
            for path in Path(product).rglob(b):
                S2_files.append(path)
    else:
        bands = ["*B12.jp2","*B11.jp2","*B05.jp2"]
        for b in bands:
            for path in Path(product).rglob(b):
                S2_files.append(path)
    if len(S2_files)>3: # check
        S2_files = S2_files[0:3]
    return S2_files      
    
        
def plot_snow(nbr,label=[],bounds=None):
    if not label:
        label = ["Title" for i in range(len(nbr))]
    images = []
    i = 0
    for nbr in nbr:
        if bounds != None:
            images.append(hv.Image(nbr,bounds=bounds).opts(cmap=cmap1,colorbar=True,title=label[i]))
        else:
            images.append(hv.Image(nbr).opts(cmap=cmap1,colorbar=True,xaxis=None,yaxis=None,title=label[i]))
        i+=1
    return images    
    
def dump_coordinates(geo_json):
    filename = "polygon.json"
    file = os.path.join(os.getcwd(),filename)
    with open(file, 'w') as fp:
        json.dump(geo_json, fp)
        print("Dump coordinates as %s"%filename)  
            
# display mean values of the computation above 
def analysis(products,arrays):
    # mask invalid values
    mask_arr = [ma.masked_invalid(a) for a in arrays]
    data = pd.DataFrame(np.nan,columns=["min","max","mean"],index=range(0,len(arrays)))
    for i in range(len(arrays)):
#         print(arrays[i].min(),arrays[i].max(),arrays[i].mean())
        data.iloc[i,0] = mask_arr[i].min()
        data.iloc[i,1] = mask_arr[i].max()
        data.iloc[i,2] = mask_arr[i].mean()
    data.index = dates(products)
    display(data)
    sns.set_style("whitegrid")
    sns.scatterplot(x=data.index,y="mean",data=data,marker="s",color="Navy")        
