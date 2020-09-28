<img src="./Trials/media/Cleope_logo.PNG" alt="drawing" width="200"/>

# Welcome to CLEOPE! 
**CLEOPE** (CLoud Earth Observation Processing Environment) is a DIAS-ONDA service of EO products discovery, manipulation and visualization via [Jupyter](https://jupyter.org/) integrated development environment.

[![N|Solid](https://www.python.org/static/community_logos/python-logo.png)](https://www.python.org/static/community_logos/python-logo.png) 
![N|Solid](https://jupyter.org/assets/main-logo.svg)
![N|Solid](https://www.onda-dias.eu/cms/wp-content/uploads/2018/06/logo_onda_retina.png)


CLEOPE is a web-based platform aimed where users can create their own Jupyter Notebooks and develop their own applications on Cloud.

As its additional value, CLEOPE offers a collection of pre-installed libraries and template notebooks to enhance users experience with the ONDA data offer. All the examples are available in a shared environment with the aim to help users to easily explore ONDA services, with particular emphasis to approaching EO cloud resources through Advanced API (ENS). 
Example notebooks provided into CLEOPE are split into two main categories:
  - a set of templates aimed at facilitating the data access on Cloud;
  - a collection of mission specific tutorials, particularly suited for educational purposes, which will help users to process EO data offered by ONDA.

More details on CLEOPE available resources provided 👉 [here](#tech).

# Table of Contents
1. [The Workspace](#workspace)
    1. [OData API provided interface](#odata_api)
    2. [Advanced API (ENS) provided interface](#ens_api)
    3. [Default directory tree](#tree)
        1. [Shared resources](#shared_r)
2. [About CLEOPE](#tech)
    1. [Resources limitations](#quotas)
        1. [Available Resources on CLEOPE *Free* account](#resources1)
        2. [Available Resources under *Premium* subscription](#resources2)
    2. [Python environment and dependencies](#pyenv)
        1. [Add modules to the local path](#add_modules)
        2. [Install additional packages via *pip*](#pip)
    3. [The ONDA Advanced API (ENS) path to products](#pseudopaths)

# The Workspace
<a id="workspace"></a>
CLEOPE **public workspace** offers collection of template notebooks aimed at easly introducing users to browse, inspect and download Copernicus products via the OData API protocol and DIAS-ONDA Advanced API (ENS). 

<img src="./Trials/media/use_case.PNG" alt="drawing" width="600"/>

## OData API provided interface
<a id="odata_api"></a>
Via their own Jupyter notebooks users can easily download ONDA products, by specifying their ONDA `username` and `password` and the desired items. The download option is supported by the [OData API](https://www.onda-dias.eu/cms/knowledge-base/odata-odata-open-data-protocol/) protocol; this allows browsing the ONDA Catalogue and then selecting and downloading EO products. All the downloaded products are stored in the 📁`local_files` folder accessible within user own CLEOPE workspace, unzipped and ready to be used.

## Advanced API (ENS) provided interface
<a id="ens_api"></a>
On the other hand the [Elastic Node Server (ENS)](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) software provides a front-end to the ONDA Data Storage  which extends traditional Object Storages API by exposing standard Directories and Files. Within CLEOPE a dedicated ENS access point exposing products in their native format is provided to users that want to directly access products and process them. Check out [here](#pseudopaths) the main guidelines to access products via ENS.

## Default directory tree
<a id="tree"></a>

![CLEOPE default tree](./Trials/media/tree.PNG)

### Shared resources
<a id="shared_r"></a>

`Trials` folder collects CLEOPE notebooks set, while the `local_files` folder is the default destination folder of products downloaded via Jupyter Notebooks. <br>

📁 `Trials/modules` folder collects the main libraries related to the set of template notebooks provided within CLEOPE workspace.
- Modules aimed at the **data access** are:
    - `catalogue.py` and `interactive_layers.py`, interfaced with the geographical research of products via Jupyter Notebook;
    - `qm.py` dedicated to the product **search**, **order** and **download** via Jupyter Notebooks. <br>
    
- Modules dedicated to **EO data processing** are scripts called in the mission dedicated notebook.
    - `cams.py`, `cgls.py` and `cmems.py` are named after the mission they are dedicated to - Copernicus Atmosphere, Copernicus Land and Copernicus Marine, respectively;
    - `data_processing_*.py` are named after the Sentinel mission of reference.<br>

Users can call the Python built-in methods to show help on CLEOPE functions, via:
- `help(<module-name>)` to display all the functions collected into each module;
- `<module-name>.<function-name>.__doc__` to display help on one single function of the module.

📁 All the other folders into the `Trials` main directory collect the trial notebooks set. More information on CLEOPE notebooks is provided 👉[here](Trials/readme.md).

# About CLEOPE
<a id="tech"></a>
CLEOPE is deployed as [The Littlest Jupyter Hub - TLJH](http://tljh.jupyter.org/en/latest/index.html) on OVH Cloud infrastructure provided with [ENS-legacy](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) and [OData API](https://www.onda-dias.eu/cms/knowledge-base/odata-odata-open-data-protocol/) provided interfaces, allowing users to directly access and process ONDA EO products.<br>
TLJH is configured with a **Python 3 kernel**, provided of an extensive Python environment aimed at EO data processing and data analysis with respect to any other default Jupyter environment, **without any local installation or additional configuration required**.

## Resource limitations
<a id="quotas"></a>

Registered users' hardware features are limited according to the subscription plan. Quotas are configured on DISK space, RAM and CPU number.

- **Disk limit** - when the threshold is exceeded an error message is printed out on screen, by both
    - command line:<br>`cp:error writing 'file': Disk quota exceeded`
    - GUI: <br><img src="Trials/media/disk_quota_err.png" alt="drawing" width="400"/>

- **RAM limit** - If users use more than the allowed amount of RAM, their notebook kernel will restart and a pop-up message is displayed:
<br><img src="Trials/media/dead_kernel.png" alt="drawing" width="400"/> <br>
No other actions are allowed on the notebook in this case. Please note that shutdown unused notebooks is supplemental to helping with memory errors.

- **CPU limit** specifies the total CPU cores that each user can use within CLEOPE workspace. If the CPU limit is exceeded, computations may become very slow.

### Available Resources on CLEOPE *Free* account
<a id="resources1"></a>

| **Disk** |**RAM**|**CPU**|
| ------------- | ------ |-------------|
|20 GB|2 GB|2|

Please note that CLEOPE free account has a limited amount of resources available, thus some notebooks potentialities may be prevented. 👉 Upgrade to *Premium* and break out computational resources limitation for a better programming experience!

### Available Resources under *Premium* subscription 
<a id="resources2"></a>

CLEOPE service can be upgraded to _Premium_ subscription according to [our commercial offer](https://www.onda-dias.eu/cms/services/catalogues/virtual-servers/#general-purpose). The increase of the available computational resources will enhance users' programming experience.

💰 **Monthly subscription upon request: please contact the [ONDA Service Desk](https://www.onda-dias.eu/cms/contact-us/) to upgrade CLEOPE!**

## Python environment and dependencies
<a id="pyenv"></a>

CLEOPE supports an extensive Python environment suited for EO data processing and data analysis purposes, shared among all registered users.<br> 
Users can consult 👉[here](Trials/readme.md#requirements) the main Python packages used in the example notebooks, already provided in CLEOPE.

### Add modules to the local path
<a id="add_modules"></a>

By default, Python looks for its modules and packages in its absolute `PATH`. Within a python script, users can add path(s) occasionally to the default path by adding the following lines in the head section of the python application or script to load additional modules:
```python
import sys
sys.path.append('/home/jupyter-user/directory')
```
For instance, for the `modules` folder in the example notebooks suite:
```python
import os, sys
sys.path.append(os.path.join(os.path.expanduser("~"),"CLEOPE/Trials/modules"))
```
In this way all the scripts contained in the `modules` folder are callable within the same Jupyter Notebook.

### Install additional packages via *pip*
<a id="pip"></a>

[*pip*](https://pip.pypa.io/en/stable/) is the package installer for Python.<br>
CLEOPE Python packages are installed to a system directory (i.e. `/opt/tljh/user/lib/python3.7/site-packages`) by default, which requires root access. <br>
CLEOPE users have not admin rights, thus they cannot install packages visible to all users. Though, opening a new terminal, users can run
```
pip install --user <package-name>
```
or also:
```
pip install --user <package-name>==<version>
```
The `--user` option makes pip install packages into users own home directory, which does not require any special privileges.<br>

⚠️ Please note that the `pip` channel requires that also all the needed dependencies are installed as well.

Once the installation is complete, additional packages are installed to users own home directory path, i.e. `/home/jupyter-user/.local/lib/python3.7/site-packages`.

## The ONDA Advanced API (ENS) path to products
<a id="pseudopaths"></a>
Within CLEOPE environment, EO cloud resources can be easily accessed via the Advanced API (ENS).<br> Products are spread into hierarchical directories given the CLEOPE mounting point:
````shell
/mnt/Copernicus/
````
Remote location of products can therefore be composed as follows:

|Mounting Point|Pseudopath|Product name|
| -------------|-------------|-------------|
`/mnt/Copernicus/`|`What/When`|`filename.ext`

where the product name extension _.ext_ will depend on the product main class. We strongly recommand to read the [ONDA official documentation](https://www.onda-dias.eu/cms/knowledge-base/adapi-path-to-products/) about ENS path to products.
