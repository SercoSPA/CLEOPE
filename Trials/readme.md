<img src="./media/Cleope_logo.PNG" alt="drawing" width="200"/>

# CLEOPE Jupyter Notebooks suite

Example notebooks provided into CLEOPE are split into two main categories:
  - a set of templates aimed at facilitating the **data access** on Cloud;
  - a collection of mission specific tutorials, particularly suited for educational purposes, with **few examples of basic processing** suited on ONDA EO data offer.

# Table of Contents

1. [ONDA data access dedicated notebooks](#main1)
    1. [Discover ENS](#discover_ENS)
    2. [Download products via Jupyter Notebook](#odata)
    3. [Order products via Jupyter Notebook](#order)
    4. [Search products by AOI via Jupyter Notebook](#search)
2. [Mission-dedicated notebooks](#mission)
    1. [Sentinel 1](#s1)
    2. [Sentinel 2](#s2)
    3. [Sentinel 3](#s3)
    4. [Sentinel 5P](#S5P)
    5. [Copernicus Atmosphere](#cams)
    6. [Copernicus Marine](#cmems)
    7. [Copernicus Land](#cland)
3. [Requirements](#requirements)

# ONDA data access dedicated trial notebooks
<a id="main1"></a>
<img src="./media/actions.PNG" alt="drawing" width="200"/>

The data access template notebooks are called as follows:
```
DISCOVER_ONDA.ipynb
ORDER.ipynb
SEARCH.ipynb
``` 
This set of trial notebooks is aimed at facilitating the data access on Cloud, in particular:
 - the way to access ONDA EO data offer via Jupyter Notebook using the [Elastic Node Server (ENS)](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/);
 - the way to download and order archived products using the [OData API](https://www.onda-dias.eu/cms/knowledge-base/odata-odata-open-data-protocol/) provided interface;
 - the way to browse geographical areas of interest via Jupyter Notebook.
 
## DISCOVER_ONDA trial notebook
<a id="discover_onda"></a>
This notebook is an easy introduction to the use of [ENS](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) and to the product download via Jupyter notebooks. Both methods allow users to access the online ONDA data offer.

### Discover ENS
<a id="discover_ENS"></a>
Within CLEOPE a dedicated ENS access point exposes products in their native format so that they are accessible to users, who can process them without any previous download. The trial notebook finds a product in the remote file system, if:
 - the single product name is given, or
 - a list of product names stored in a 📄`.txt` file is given.
 
📌 The remote position (i.e. _pseudopath_) of products is saved into a temporary file into 📁`resources`.<br>
⚠️ A warning message is raised if any of the input products show the `offline` status set to `True`, meaning that the product is not still available to ENS browsing.<br> In this case 📑 `ORDER.ipynb` ready-to-use notebook is suited for ordering archived products.

### How to download products
<a id="odata"></a>
Alternatively to ENS, users can call the `download` function to perform a download of products via their own Jupyter Notebook. The function is written in the 📄`qm.py` script, which can be called anywhere in users own workspace as long as its path is imported:
````python
import os, sys
sys.path.append(os.path.join(os.path.expanduser("~"),"Trials/modules"))
import qm
qm.download(product,"onda_username","onda_password")
````
where the product field is the requested item.
Users need to specify their ONDA username and password and the product name they are interested in, including its native format (e.g. zip, netCDF).<br>
Similarly, users can download products recursively from a custom list given as input of the `download_list` function:
````python
import os, sys
sys.path.append(os.path.join(os.path.expanduser("~"),"Trials/modules"))
import qm
qm.download_list("product_list.txt","onda_username","onda_pswd")
````
Also in this case the native file format of products in the list must be specified explicitly.

## ORDER trial notebook
<a id="order"></a>
This trial notebook provides the possibility to order an archived product via Jupyter. Archived products, in fact, are not available to ENS browsing nor to the download via 🌍ONDA Catalogue. <br>👉 [Read more on ONDA Catalogue](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-overview/).<br>
Given the product name as input, `ORDER.ipynb` notebook orders the product via [OData HTTP POST protocol](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-via-odata-api/), suited to perform this kind of action. A progress bar is displayed for checking the time left; no worry if the action may take up a few minutes more to be completed as this includes the time needed to refresh ENS as well. <br>
Please note that the product restoration is automatically performed if users try to call the `download` function on an archived product.

## SEARCH trial notebook
<a id="search"></a>
This trial notebook allows the geographical search of ONDA EO data offer by simutating a small 🌍ONDA Catalogue via Jupyter Notebook. The geographical search works with few simple steps:
 1. ✏️ Select an area of interest on a map drawing a rectangle, a polygon or a polyline. The selected geo-coordinates are saved in a 📄`.json` file;
 2. ✔️ (optional) select mission, product type and sensing range filters. Please note that in case many results are expected, the performace can be impacted, so it is strongly recommended to set filters on;
 3. 🌐 Visualize products footprint layers on the map;
 4. 📝 (optional) save a batch of selected products in a dedicated text file located by default into the `outputs` folder. 
     1. This product list can be optionally converted into a ENS-compliant product list ([Discover ENS](#discover_ENS)) or users can choose to download products via their own notebook ([How to download products](#odata)).

# Mission dedicated trial notebooks
<a id="mission"></a>
This collection of trial notebooks has been published with the purpose of leading users into basic operations of data processing of EO products exploiting the ONDA data offer in a few mission dedicated tutorials. The current CLEOPE version supports:
 - 🌱 Land/Water monitoring applications
 - 🏭 Atmospheric monitoring applications 
 
both using Sentinels and Copernicus Services products. 

## S1 trial notebook
<a id="s1"></a>
[![N|Solid](https://earth.esa.int/image/image_gallery?uuid=23f73931-c1c7-4013-a7dc-fb506ff182e2&groupId=10174&t=1354275607606)](https://earth.esa.int/image/image_gallery?uuid=23f73931-c1c7-4013-a7dc-fb506ff182e2&groupId=10174&t=1354275607606)

Sentinel-1 trial notebook is a useful introduction to Sentinel-1 data processing aimed at detecting changes in the environment via the backscattering differences. Particular focus is given to:
- the visualisation of the built-up area extended near Wuhan, where a new hospital has been built in 10 days during the COVID-19 emergency.
- ships detection near Trieste (Italy) harbour.

To this aim the S1 L1 Ground Range Detected (GRD) products with high resolution (H), with different sensing dates. Images are clipped over custom-selected coordinates and plot out on screen side-by-side, normalised over the backscattering coefficient color in order to allow users to easily detect changes in the images. <br>✏️ S1 dataframes are customisable according to users choices, as for the coordinates needed to clip data. In the default CLEOPE workspace the sample list of example products is provided, but some of these products could be *offline* and must be ordered first.

## S2 trial notebook
<a id="s2"></a>
[![N|Solid](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)

Sentinel-2 trial notebook is a useful introduction to Sentinel-2 products tile processing.
The module `data_processing_S2_affine` unpack raster data and perform a coordinates reprojection to allow optional clips on the image. Examples are based on popular RGB compositions (true color, false color IR and false color NIR) and on index computations. <br>
The computation of the following indexes is performed:
- the _Normalised_ _Burnt_ _Index_ to detect burnt areas;
- the _Normalised Difference Water Index_ aimed at detecting floating plastic in the sea;
- the _Normalised_ _Difference_ _Snow_ _Index_ to easily differentiate snow coverage from clouds.

Optionally, users can compute other indexes via the combination of `bands` and `ratio` functions provided in the suite, given an input resolution. All Sentinel-2 bands are at users disposal to this aim. The generated plots are geo-referenced through the extraction of coordinates from raster data.<br> 
✏️ The dataframe of S2 tiles is customisable according to users choices. In the default CLEOPE workspace a sample list of products is provided on the example detailed above. Some of these products could be *offline* and must be ordered first.

## S3 trial notebook
<a id="s3"></a>
[![N|Solid](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)

### OLCI L2 LFR-WFR
Sentinel-3 OLCI trial notebook is an introduction to the processing and visualization of Sentinel-3 OLCI Full Resolution Land and Water product types (LFR and WFR), allowing a colormap visualization of the extracted datasets.
With this notebook users can load OLCI LFR and WFR products, collected into separated lists, extract the data sets to re-arranging and concatenating them together to obtain a final 3d data array which depth is the new _time_ dimension. Users can also specify bounds as `xmin,xmax,ymin,ymax` to create a custom subset.
The visualisation of the variables of interest is displayed in an interactive geo-referenced plot. <br>
The following table shows the possible variables available in the notebook. Possible choices vary according to the OLCI product type.

| _LFR_ | _WFR_ |
| --- | --- |
| `OTCI` OLCI Terrestrial Clorophyll Index| `TSM_NN` Total suspended matter concentration (Neural Net)|
| `OGVI` OLCI Global Vegetation Index | `CHL_OC4ME` Algal pigment concentration|
| `IWV` Integrated water vapour column above the current pixel|`CHL_NN` Algal pigment concentration (Neural Net)|
||`IWV` Integrated water vapour column above the current pixel|

✏️ The dataframe of S3 products is customisable according to users choices. In the default CLEOPE workspace a sample list of OLCI products is provided. Some of these products could be *offline* and must be ordered first.

### SLSTR RBT L1b
S3 SLSTR trial notebook is a case study focused on the monitoring of the fire developed near Chernobyl on 4/04/2020. Flames burnt for several days all around the area surrounding the abandoned nuclear power plant, enhancing the risk of emanating radioactive particles. In this trial notebook S3 SLSTR radiometric measurements are used, extracted from L1b products as radiances at the top of the atmosphere (TOA), with the purpose to detect some transient radiation indicating the presence of radioactivity in the area of interest.<br>
This trial notebook makes use of a module developed for [S5P trial notebook](#S5P) which is helpful in selecting the clip boundaries from the CO emission associated to the fire, being a clear example of synergy between trial notebooks powered by CLEOPE.

✏️ In this example the sample list of S3 products is very oriented on the case study under exam but in principle users can customise this data set according to their own scientific specifications. Some of these products could be *offline* and must be ordered first.

### SLSTR LST L2
S3 SLSTR LST trial notebook is focused on the treatment and visualisation of S3 land surface temperature products, taking the Siberian heat wave on June 2020 as a case study. <br>
With this notebook users can load SLSTR LST products, extract the data sets to be re-arranged into a final product, showing geo-coordinates and LST information merged. <br>
The land surface temperature over the area of interest is displayed in color-adjusted geo-referenced plot. This trial notebook makes use of a module developed for [S5P trial notebook](#S5P) which is helpful in selecting the clip boundaries from the CO emission associated to any wildfires areas (i.e. associated to the siberian heat wave case study), being a clear example of synergy between trial notebooks powered by CLEOPE.

✏️ The dataframe of S3 products is customisable according to users choices. In the default CLEOPE workspace a sample list of SLSTR LST products is provided. Some of these products could be *offline* and must be ordered first.

## S5P trial notebook 
<a id="S5P"></a>
[![N|Solid](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)

Sentinel-5P trial notebook is an introduction about the composition of stacked frames of TROPOMI L2 variables CH4, NO2, O3, HCHO, SO2 and CO in a geo-referenced plot. Input data sets can be cut by taking the input vertexes.<br>
Sentinel-5P tutorial is developed into two case study taken under analysis.
1. The carbon monoxide (CO) variation over the western Australia, hit by several fire episodes during December 2019 and January 2020;
2. The nitrogen dioxide (NO2) overall decline over Italy due to the lockdown emergency of COVID-19 during February/March 2020;
3. The sulfure dioxide (SO2) transient concentration over the Anak Krakatoa volcano (Indonesia), which awoke on 12/04/2020.

✏️ The dataframe of S5P dataframes is customisable according to users choices. In the default CLEOPE workspace a sample list of products is provided, suited on the case studies described above. Some of these products could be *offline* and must be ordered first.

## CAMS trial notebook
<a id="cams"></a>

<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Atmosphere-hover.png?itok=rc5-OANv" width="100" height="100" />

ONDA provides access to data and tools related to the Copernicus Atmosphere Monitoring Services with an extensive catalogue of products coming from a variety of sources. These products are released in the form of maps and charts, being an ensemble of air quality models processed by diverse data centres. <br>
The CAMS oriented trial notebook is an interactive tool aimed at data visualisation of _Analysis_ _Surface Fields_ products, powered by ENS. Users can interactively choose a period of interest and a sampling frequency within it (i.e. days, weeks or months) and visualise the interactive global layers of nitrogen dioxide, carbon monixide, sulfure dioxide, methane, ethane, propane, isoprene, hydrogen peroxide, formaldehyde, nitric acid, nitrogen monoxide, hydroxide and peroxyacyl nitrates.<br>
By default this example notebook is powered by ENS.

## CMEMS trial notebook
<a id="cmems"></a>

<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Marine-hover.png?itok=0bCGpFuu" width="100" height="100" />

ONDA provides access to the Copernicus Marine Services data sets of ocean products derived from satellite and in situ observation, suited for science and global monitoring purposes. <br>
CLEOPE CMEMS trial notebook is an interactive tool aimed at data visualisation of _Global Ocean Analysis_ Sea Surface Temperature products exploiting the power of ENS. Users can choose a period of interest and a sampling frequency within it (i.e. days, weeks or months), concatenate datasets and visualise interactive timeseries color mapped layers. <br>
By default this example notebook is powered by ENS.

## CGLS trial notebook
<a id="cland"></a>

<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Land-hover.png?itok=LuSkXVw2" width="100" height="100" />
The Copernicus Global Land Service (CGLS) is part of ONDA data offer and systematically produces a series of qualified bio-geophysical products on the status and evolution of the land surface, at global scale at mid spatial resolution. <br>
CLEOPE CGLS trial notebook allows the visualisation of interactive vegetation coverage maps, powered by ENS, by choosing a variable of interest indicating the vegetation status, e.g. the NDVI, the  Fraction of Absorbed Photosynthetically Active Radiation, the Fraction of green vegetation cover and the Leaf Area Index.

# Requirements
<a id="requirements"></a>

Trial notebooks make the use of packages and modules that do not come as part of the standard Python library, so CLEOPE is provided with additional modules specifically related to each one. Main Python modules associated to each notebook are collected in the Table below.

| | processing|visualization|
| ------------- | ------ |-------------|
| S1| `GDAL`,`xarray`,`cv2`,`PIL`,`skimage`,`imutils`| `matplotlib`|
| S2| `rasterio`,`cv2`,`xarray`| `matplotlib`,`hvplot`|
| S3| `xarray`|`cartopy`,`hvplot`|
| S5P|`xarray`|`cartopy`,`matplotlib`|
| CAMS|`xarray`|`cartopy`,`hvplot`|
| CMEMS|`xarray`|`cartopy`,`hvplot`|
| CGLS|`xarray`|`cartopy`,`hvplot`|
| DISCOVER_ONDA|`requests`| |
| ORDER|`requests`| |
| SEARCH|`requests`|`ipyleaflet`|

## Note on CLEOPE _Free_ account
CLEOPE *Free* account has a limited amount of resources available, thus some basic functionalities are prevented due to [resource limitations](../readme.md#resources1). <br>
Find here below which notebooks are suited on your needs.

| | CLEOPE Free | CLEOPE Premium|
| ------------- | ------ |-------------|
| CAMS_notebook|✔️ | ✔️|
|CGLS_notebook_DMP| ✔️|✔️|
|CGLS_notebook|✔️|✔️|
| CMEMS_notebook| ✔️| ✔️|
|DISCOVER_ONDA|✔️|✔️|
|ORDER|✔️|✔️|
|SEARCH|✔️|✔️|
|S1_notebook_LULC|✔️|✔️|
|S1_notebook_ships|✔️|✔️|
|S2_notebook_fires|✔️|✔️|
|S2_notebook_oil|✔️|✔️|
|S2_notebook_plastic|✔️|✔️|
|S2_notebook_snow|✔️|✔️|
|S3_OLCI_notebook|❌|✔️|
|S3_SLSTR_notebook|❌|✔️|
|S3_LST_notebook|✔️|✔️|
|S5P_notebook-AUS|✔️|✔️|
|S5P_notebook-IT|✔️|✔️|
|Krakatoa_notebook|✔️|✔️|

