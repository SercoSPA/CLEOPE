# ONDA data access dedicated trial notebooks

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
This notebook is an easy introduction to the use of [ENS](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) and to the product download via Jupyter notebooks. Both methods allow users to access the online ONDA data offer.

### Discover ENS
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
qm.download(product,"onda_username","onda_pswd")
````
where the product field is the requested item.
Users need to specify their ONDA username and password and the product name they are interested in, including its native format (i.e. zip, netCDF).

## ORDER trial notebook
This trial notebook provides the possibility to order an archived product via Jupyter. Archived products, in fact, are not available to ENS browsing nor to the download via 🌍ONDA Catalogue. <br>👉 [Read more on ONDA Catalogue](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-overview/).<br>
Given the product name as input, `ORDER.ipynb` notebook orders the product via [OData HTTP POST protocol](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-via-odata-api/), suited to perform this kind of action. A progress bar is displayed for checking the time left; no worry if the action may take up to 30 minutes to be completed!🕕🕡 It includes the time needed to refresh ♻️ ENS as well.  

## SEARCH trial notebook
This trial notebook allows the geographical search of ONDA EO data offer by simutating a small 🌍ONDA Catalogue via Jupyter Notebook. The geographical search works with few simple steps:
 1. ✏️ Select an area of interest on a map drawing a rectangle, a polygon or a polyline. The selected geo-coordinates are saved in a 📄`.json` file;
 2. ✔️ (optional) select mission, product type and sensing range filters. Please note that in case many results are expected, the performace can be impacted, so it is strongly recommended to set filters on;
 3. 🌐 Visualize products footprint layers on the map;
 4. 📝 (optional) save a batch of selected products in a dedicated file named `list.txt` located by default into the `outputs` folder (but any other destinations are allowed within users own workspace).

# Mission dedicated trial notebooks
<a id="mission"></a>
This collection of trial notebooks has been published with the purpose of leading users into data processing of EO products exploiting the ONDA data offer in a few mission dedicated tutorials. The current CLEOPE version supports:
 - 🌱 Land monitoring applications (S1, S2 and S3)
 - 🏭 Atmospheric monitoring applications (S5P and Copernicus Atmosphere Monitoring Services)

## S1 trial notebook
[![N|Solid](https://earth.esa.int/image/image_gallery?uuid=23f73931-c1c7-4013-a7dc-fb506ff182e2&groupId=10174&t=1354275607606)](https://earth.esa.int/image/image_gallery?uuid=23f73931-c1c7-4013-a7dc-fb506ff182e2&groupId=10174&t=1354275607606)

Sentinel-1 trial notebook is a useful introduction to Sentinel-1 data processing aimed at finding new build-up areas, in order to monitor how the urban sprawl is changing the environment. Sentinel-1 trial notebook is dedicated to the visualisation of the built-up area extended near Wuhan, where a new hospital has been built in 10 days during the COVID-19 emergency. <br>
To this aim the S1 L1 Ground Range Detected (GRD) products with high resolution (H), sensed before and after the building site in order to detect the environmental changes. Images are clipped over custom-selected coordinates and plot out on screen side-by-side, normalised over the backscattering coefficient color in order to allow users to easily detect landcover changes. <br>✏️ The dataframe of S1 products is customisable according to users choices, as for the coordinates needed to clip data. In the default CLEOPE workspace the sample list of example products is provided.

## S2 trial notebook
[![N|Solid](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)

Sentinel-2 trial notebook is a useful introduction to Sentinel-2 products processing. 
This notebook loads a custom list of products, which can be the one saved in `SEARCH.ipynb`, and filters the S2 products. Module `data_processing_S2` directly finds products pseudopath and unpack raster data with the purposes of:
 - Compose and visualize a true RGB stack in a few computational steps:
    - open S2 red, green and blue channels as raster data matrixes;
    - compose the 3D matrix of colors;
    - equalize the image
    - show the image. 📷
 - Compose and visualize the _Normalised_ _Burnt_ _Index_ (NBR) on a timeseries. This operation is interesting if applied on a dataframe containing the same S2 tile subject to hard changes in the vegetation richness (e.g fires 🔥) on different sensing dates, so that to detect changes in the vegetation water content. 
 - Compose and visualise a false color image (using SWIR and NIR bands) aimed at enhancing the snow coverage on the image representation. Computational steps are identical to the RGB stack.
 - Compose and visualise the _Normalised_ _Difference_ _Snow_ _Index_ (NDSI) on a timeseries. This computation is interesting if applied on the same area analysed during different seasons so that it is possible to see changes in the snow/ice ❄️ content. 

All generated plots are geo-referenced, through the extraction of coordinates from raster data.<br> 
✏️ The dataframe of S2 tiles is customisable according to users choices. In the default CLEOPE workspace a sample list of examples is provided.

## S3 trial notebook
[![N|Solid](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)

### OLCI L2 LFR-WFR
Sentinel-3 OLCI trial notebook is an introduction to the processing and visualization of Sentinel-3 OLCI Full Resolution Land and Water product types (LFR and WFR), allowing a colormap visualization of the extracted datasets.
With this notebook users can load OLCI LFR and WFR products, collected into separated lists, extracting the data sets through the `xarray` Python package; data sets are re-arranged and concatenated together into a final 3d data array which depth is the new _time_ dimension. Users can also specify bounds as `xmin,xmax,ymin,ymax` to create a custom subset over these vertexes.
Finally the visualisation of the variables of interest is displayed in a dynamical and interactive geo-referenced plot. <br>
The following table shows the possible variables available in the notebook. Possible choices vary according to the OLCI product type.

| _LFR_ | _WFR_ |
| --- | --- |
| `OTCI` OLCI Terrestrial Clorophyll Index| `TSM_NN` Total suspended matter concentration (Neural Net)|
| `OGVI` OLCI Global Vegetation Index | `CHL_OC4ME` Algal pigment concentration|
| `IWV` Integrated water vapour column above the current pixel|`CHL_NN` Algal pigment concentration (Neural Net)|
||`IWV` Integrated water vapour column above the current pixel|

✏️ The dataframe of S3 products is customisable according to users choices. In the default CLEOPE workspace a sample list of OLCI products is provided.

### SLSTR RBT L1b
S3 SLSTR trial notebook is a case study focused on the monitoring of the fire developed near Chernobyl on 4/04/2020. Flames burnt for several days all around the area surrounding the abandoned nuclear power plant, enhancing the risk of emanating radioactive particles. In this trial notebook S3 SLSTR radiometric measurements are used, extracted from L1b products as radiances at the top of the atmosphere (TOA), with the purpose to detect some transient radiation indicating the presence of radioactivity in the area of interest.<br>
This trial notebook makes use of a module developed for [S5P trial notebook](#S5P) which is helpful in selecting the clip boundaries from the CO emission associated to the fire, being a clear example of synergy between trial notebooks powered by CLEOPE.

✏️ In this example the sample list of S3 products is very oriented on the case study under exam but in principle users can customise this data set according to their own scientific specifications.

## S5P trial notebook 
<a id="S5P"></a>
[![N|Solid](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)

Sentinel-5P trial notebook is an introduction about the composition of stacked frames of TROPOMI L2 variables in a geo-referenced plot. The notebook loads a list of custom products, which can be the one saved via the `SEARCH.ipynb`, filtering the following TROPOMI L2 variable of interest: CH4, NO2, O3, HCHO, SO2 and CO. Input data sets are then cut by taking as input the vertexes dumped in `polygon.json` reference file, which descends from the `SEARCH.ipynb` notebook (i.e. ✏️ it is the drawn rectangle). In general this operation may induce a loss of resolution in the data visualization since no mosaicing technique is performed on data sets at this level. It is useful, though, due to the hugeness of S5P footprints. <br>
Sentinel-5P tutorial is developed into two case study taken under analysis.
1. The carbon monoxide (CO) variation over the western Australia, a region which was hit by several fire episodes during December 2019 and January 2020;
2. The nitrogen dioxide (NO2) overall decline over Italy due to the lockdown during the emergency of COVID-19 virus in February/March 2020;
3. The sulfure dioxide (SO2) transient concentration over the Anak Krakatoa volcano, located in the Sonda strait between Sumatra and Java islands in Indonesia, which awoke on 12/04/2020.

✏️ The dataframe of S5P dataframes is customisable according to users choices. In the default CLEOPE workspace a sample list of products is provided, suited on the cases of study described above.

## CAMS trial notebook
<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Atmosphere-hover.png?itok=rc5-OANv" width="100" height="100" />

ONDA provides access to data and tools related to the Copernicus Atmosphere Monitoring Services with an extensive catalogue of products coming from a variety of sources. These products are released in the form of maps and charts, being an ensemble of air quality models processed by diverse data centres. <br>
The CAMS oriented trial notebook is an interactive tool aimed at data visualisation of _Analysis_ _Surface Fields_ products, powered by ENS. Users can choose a period of interest and a sampling frequency within it (i.e. days, weeks or months), slicing the map in the way of need. 

## CMEMS trial notebook
<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Marine-hover.png?itok=0bCGpFuu" width="100" height="100" />

ONDA provides access to the Copernicus Marine Services data sets of ocean products derived from satellite and in situ observation, suited for science and global monitoring purposes. <br>
CLEOPE CMEMS trial notebook is an interactive tool aimed at data visualisation of _Global Ocean Analysis_ products exploiting the power of ENS. Users can choose a period of interest and a sampling frequency within it (i.e. days, weeks or months), visualising interactive layers on the map.

## CGLS trial notebook
<img src="https://www.copernicus.eu/sites/default/files/styles/servicecards_icon_hover/public/2018-10/Land-hover.png?itok=LuSkXVw2" width="100" height="100" />
The Copernicus Global Land Service (CGLS) is part of ONDA data offer and systematically produces a series of qualified bio-geophysical products on the status and evolution of the land surface, at global scale at mid spatial resolution. <br>
CLEOPE CGLS trial notebook is an interactive tool aimed at visualising an interactive map of vegetation coverage, powered by ENS. Users can choose a variable indicating the vegetation status to produce an interactive land map.

# Requirements
Trial notebooks make the use of packages and modules that do not come as part of the standard Python library, so CLEOPE is provided with additional modules specifically related to each one. Main Python modules associated to each notebook are collected in the Table below.

| | processing|visualization|
| ------------- | ------ |-------------|
| `S1`| `GDAL`,`xarray`| `matplotlib`|
| `S2`| `rasterio`,`cv2`| `matplotlib`,`holoviews`|
| `S3`| `xarray`| `hvplot`,`matplotlib`|
| `S5P`|`netCDF4`|`holoviews`|
| `CAMS`|`xarray`|`hvplot`|
| `CMEMS`|`xarray`|`hvplot`|
| `CGLS`|`xarray`|`hvplot`|
| `DISCOVER_ONDA`|`requests`| |
| `ORDER`|`requests`| |
| `SEARCH`|`requests`|`ipyleaflet`|

Moreover, CLEOPE supports the possibility to install complementary or additional libraries. <br>👉 [Read how to do here](../readme.md#packages).

