[![N|Solid](https://www.onda-dias.eu/cms/wp-content/uploads/2018/06/logo_onda_retina.png)](https://www.onda-dias.eu/cms/)

# Welcome to CLEOPE! 
In the framework of ONDA-DIAS, **CLEOPE** (CLoud Earth Observation Processing Environment)  is a service of EO products discovery, manipulation and visualization via interactive Jupyter notebooks supported by Python 3 kernel language.

[![N|Solid](https://www.python.org/static/community_logos/python-logo.png)](https://www.python.org/static/community_logos/python-logo.png) [![N|Solid](https://jupyter.org/assets/main-logo.svg)](https://jupyter.org/assets/main-logo.svg)

CLEOPE consists in a collection of pre-installed libraries and template notebooks to enhance users experience with ONDA data offer. All the examples are available in a shared environment with the aim to help users to easily explore ONDA services main functionalities, to learn how to access data and the way to approach EO cloud resources through Advanced API (ENS). 
Example notebooks are read and executable only. They are split into two main categories:
  - a set of templates aimed at facilitate the data access on Cloud;
  - a collection of mission specific tutorials, particularly suited for educational purposes, which will help users to process EO data offered by ONDA.

# The Workspace
In CLEOPE **public workspace** users find a first set of trial notebooks aimed at easly introducing users to ENS browsing/inspection functionalities and a series of working folders.

Data access trial notebooks are called as follows and more details are provided [here](./notebooks.md).
```
FIND_PSEUDOPATH.ipynb
ORDER.ipynb
SEARCH.ipynb
``` 
### Modules
Folder containing the main libraries related to the set of templates dedicated to the data access available to users.
- `aoi.py`: collects the `http` queries related to geographic search notebook;
- `buttons.py`: read and write in the `output` folder all the users selections;
- `empty.py`: function called by `buttons` module to remove files from the `output` directory;
- `qm.py`: collects the `http` queries related to the product order notebook.

### Output and resources 
Folders sharing temporary data (i.e. logs) and sample inputs for trial notebooks. 

### S2, S3 and S5P
Folders collecting mission specific trial notebooks, showing some type of processing of Sentinel-2, Sentinel-3 and Sentinel-5P EO products. 
Full explanation of mission specific trial notebooks is given [here](./notebooks.md). 
