# Python 3 Packages
Users can call 
```python
!pip list
```
shell command directly into a notebook cell in order to list all the installed packages and version. 
New packages can be easily installed running:
```python
!pip install <package_name>
```
or specifying the version
```python
!pip install <package_name>==<version>
```
# Add modules to local path
By default, Python looks for its modules and packages in its absolute `PATH`. Within a python script, you can add path(s) occasionally to the default path by adding the following lines in the head section of your python application or script:
```python
import sys
sys.path.append('/home/jupyter-user/directory')
```

