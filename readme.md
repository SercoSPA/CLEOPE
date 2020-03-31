[![N|Solid](https://www.onda-dias.eu/cms/wp-content/uploads/2018/06/logo_onda_retina.png)](https://www.onda-dias.eu/cms/)

# Welcome to CLEOPE! 
**CLEOPE** (CLoud Earth Observation Processing Environment) is a DIAS-ONDA service of EO products discovery, manipulation and visualization via interactive Jupyter notebooks supported by Python 3 kernel language.

[![N|Solid](https://www.python.org/static/community_logos/python-logo.png)](https://www.python.org/static/community_logos/python-logo.png) 
[![N|Solid](https://jupyter.org/assets/main-logo.svg)](https://jupyter.org/assets/main-logo.svg)

CLEOPE consists in a collection of pre-installed libraries and template notebooks to enhance users experience with ONDA data offer. All the examples are available in a shared environment with the aim to help users to easily explore ONDA services main functionalities, to learn how to access data and the way to approach EO cloud resources through Advanced API (ENS). 
Example notebooks are read and executable only. They are split into two main categories:
  - a set of templates aimed at facilitating the data access on Cloud;
  - a collection of mission specific tutorials, particularly suited for educational purposes, which will help users to process EO data offered by ONDA.

# The Workspace
CLEOPE **public workspace** offers collection of template notebooks aimed at easly introducing users to browse, inspect and download products via the OData API protocol or using DIAS-ONDA Advanced API (ENS). 

![image info](./Trials/media/use_case.PNG)

### OData API provided interface
Via their own Jupyter notebooks users can easily download ONDA products, by specifying their ONDA `username` and `password` and the desired item within the data offer. The download option is supported by the [OData API](https://www.onda-dias.eu/cms/knowledge-base/odata-odata-open-data-protocol/) protocol, an interface exposed by the Catalogue which allows browsing, selecting and downloading EO products in the Catalogue itself. Downloads are stored in the 📁 `local_files` folder within users own CLEOPE workspace, unzipped and ready to be used.

### Advanced API (ENS) provided interface
On the other hand the [Elastic Node Server (ENS)](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) software provides a simple and scalable front-end to the ONDA Data Storage on cloud which extends traditional Object Storages by exposing standard Directories and Files. Within CLEOPE a dedicated ENS access point exposing products in their native, unchanged format, is accessible to users that want to directly access products to process them (i.e. _legacy mode_). 

The data access template notebooks are called as follows and more details are provided [here](./notebooks.md).
```
DISCOVER_ONDA.ipynb
ORDER.ipynb
SEARCH.ipynb
``` 
## Modules devoted to ONDA data access
📁 `modules` folder collects the main libraries related to the set of template notebooks aimed at guiding users to the data access.<br>

📄 `aoi.py`, `buttons.py` and `empty.py` are specific scripts interfaced with the geographical research of products via Jupyter Notebook; <br>
📄 `qm.py` is a module devoted to the product **search**, **order** and **download** via Jupyter Notebook. 

## Output and resources folders
📁 Folders sharing temporary data (i.e. logs) and sample inputs for the template notebooks set. 

### S2, S3, S5P, cams
📁🌎🌍🌏 Folders collecting mission specific notebooks, showing some type of processing of Sentinel-2, Sentinel-3 and Sentinel-5P EO products. 
Full explanation of mission specific trial notebooks is given [here](Trials/user_guide.md). 
