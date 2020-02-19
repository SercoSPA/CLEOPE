## ONDA data access dedicated trial notebooks :key:
### FIND_PSEUDOPATH
This notebook introduces users to ENS showing how find ONDA products, given the product name. 
Inputs:
 - a single product name, or
 - a list of product names in a `.txt` file   

Pseudopaths list is saved into a temporary file stored into `resources` folder.

A warning message is raised if any of the input products show the `offline` status set to `True`, meaning that the product is stored in the Cloud Archive. In this case archived products can be easily accessed using the `ORDER.ipynb` ready-to-use trial.

### ORDER
This trial notebook provides the possibility to order the product from Cloud Archive via Jupyter.
Given an input product name, `ORDER.ipynb` orders the product by using an API. A progress bar is displayed for checking the time left. 

### SEARCH
This trial notebook allows the geographical search of ONDA products via Jupyter in few simple steps:
 1. Select an area of interest on a map drawing a rectangle, a polygon or a polyline. The selected geo-coordinates are saved in a `.json` file;
 2. (optional) select mission, product type and sensing range filters. Please note that in case many results are expected, the performace can be impacted, so it is strongly recommended to set as much filters as possible;
 3. Visualize products footprint layers on the map;
 4. (optional) save a batch of selected products in a dedicated file named `list.txt` located by default into the `outputs` folder or choose a destination folder in the workspace.

## Mission dedicated templates :earth_americas:
This collection of trial notebooks has been published with the purpose of leading users into data processing of EO products exploiting the ONDA data offer.
This version supports three dedicated templates for Sentinel-2, Sentinel-3 and Sentinel-5P missions. 

### S2
[![N|Solid](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)

Sentinel-2 trial notebook is a useful introduction to Sentinel-2 products processing. 
This notebook load the list of products saved in `SEARCH.ipynb` (or a custom list, but saved as `list.txt`) and filters the S2 products. Module `data_processing` directly finds products pseudopath and unpack raster data with the purposes of:
 - Compose and visualize a true RGB stack in a few computational steps:
    - open S2 red, green and blue channels as raster data matrixes;
    - compose the 3D matrix of colors;
    - equalize the image
    - show the image in a geo-referenced figure. 
   This can be easily achieved by running the function `image ` on the product previously chosen through the dropdown widget.
 - Compose and visualize the _Normalized_ _Burnt_ _Index_ (NBR) on a timeseries. This operation is interesting if applied on a dataframe containing the same S2 tile subject to hard changes in the vegetation richness (e.g fires) on different sensing dates, so that to detect changes in the vegetation water content. 

### S3
[![N|Solid](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)

Sentinel-3 trial notebook introduces to processing and visualization of Sentinel-3 OLCI Full Resolution Land and Water product types (LFR and WFR), rispectively unpacked through `land` and `water` functions, allowing a colormap visualization of the datasets.
The notebook loads the list of products saved in `SEARCH.ipynb` (or a custom list, but saved as `list.txt`), filters the S3 OLCI FR products and visualize in a geo-referenced plot the variables of interest. 

The following table shows the possible variables available in the notebook.

| `land`       |   | `water`       | | 
| ------------- | ------ |-------------|-------------|
| OTCI     | _OLCI_ _Terrestrial_ _Chlorophyll_ _Index_| TSM | _Total_ _Suspended_ _Matter_ |
|OGVI      |_OLCI_ _Global_ _Vegetation_ _Index_ | CHL_OC4ME |Algal Pigment Concentration  |
| | |IWV | _Integrated_ _Water_ _Vapour_|



### S5P 

[![N|Solid](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)

Sentinel-5P trial notebook is a gentle introduction on the composition of stacked frames of TROPOMI L2 variables in a geo-referenced plot. Products and polygon vertexes selected in the `SEARCH.ipynb` are rispectively loaded from `list.txt` and `polygon.json` output files, which one is used to cut data. Please note that the cut induces a loss of resolution in the data visualization since no mosaicing technique is performed on data sets at this level.
Provided the input list, all the TROPOMI L2 variables are allowed in the selection: CH4, NO2, O3, HCHO, SO2 and CO.

## Read more
Trial notebooks make the use of packages and modules that don't come as part of the standard Python library, so CLEOPE is provided with additional modules specifically related to each one.

| | processing|visualization|
| ------------- | ------ |-------------|
| `S2`| `rasterio`,`cv2`| `matplotlib`,`holoviews`|
| `S3`| `netCDF4`| `matplotlib`|
| `S5P`|`netCDF4`|`holoviews`|
| `SEARCH`|`requests`|`ipyleaflet`|
| `ORDER`|`requests`| |

Moreover, CLEOPE supports the possibility to install complementary or additional libraries. Read more details [here](./details.md) .

