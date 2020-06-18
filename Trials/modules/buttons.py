# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:10:29 2020

@author: GCIPOLLETTA
"""
from ipywidgets import widgets, interact, Layout, interactive
from IPython.display import display
import pandas as pd
import numpy as np
import json, os, glob

def clearall(file):
    if os.path.exists(file):
        os.remove(file)
        
# clear workspace logs 
pfiles = glob.glob(os.path.join(os.getcwd(),"outputs/product_list*.txt"))
if pfiles:
    for f in pfiles:
        clearall(f)

def remove(file):
    if os.path.exists(file):
        os.remove(file)

def write_click(item,filename=os.path.join(os.getcwd(),"outputs/product_list.txt")):
    with open(filename,"a+") as f:
        f.write(item+"\n")
#         f.write("/mnt/Copernicus/"+item+"\n")
        print("File with products created as: %s"%filename)

class select_product(object):
    def __init__(self, dataframe):
        self.filenames = [f for f in dataframe.iloc[:,1]]
        self.pseudopath = [p for p in dataframe.iloc[:,2]]
        tmp_tuple = tuple(self.filenames)
        self.file_dict = {}
        for i in range(dataframe.shape[0]):
            temp = {tmp_tuple[i]:i}
            (self.file_dict).update(temp)

    def _create_widgets(self):
        self.sel_file = widgets.SelectMultiple(description='Product',
                                               options=self.filenames,
                                               value=[self.filenames[0]],
                                               layout = Layout(width="100%"),
                                              )
        self.button = widgets.Button(description="Submit")
        self.button.on_click(self._on_button_clicked)

    def _on_button_clicked(self, change):
        self.out.clear_output()
        self.df_objects = {} 
        with self.out:
            for f in self.sel_file.value:
                self.df_objects[f] = self.file_dict[f]
                k = self.file_dict[f]
                print("Find using ENS at pseudopath:\n%s"%os.path.join(self.pseudopath[k],f))
                write_click(f)
#                 write_click(os.path.join(self.pseudopath[k],f))
                

    def display_widgets(self):
        self._create_widgets()
        self.out = widgets.Output()  # this is the output widget in which the df is displayed
        display(widgets.VBox(
                            [
                                self.sel_file,
                                self.button,
                                self.out
                            ]
                        )
               )

    def get_df_objects(self):
        return self.df_objects    


def sensing():  
    sensing_start = widgets.DatePicker(
        description = 'Sensed from:',
        disabled = False)
    
    sensing_stop = widgets.DatePicker(
        description = 'Sensed to:',
        disabled = False)
    return sensing_start,sensing_stop

def mission():
    options = {'All':["-"],
               'Sentinel-1':["All S1","SLC","GRD","OCN","RAW"], 
               'Sentinel-2':["All S2","S2MSI1C","S2MSI2A","S2MSI2Ap"],
               'Sentinel-3':["All S3","SR_1_SRA___","SR_1_SRA_A_",
                             "SR_1_SRA_BS","SR_2_LAN___",
                             "OL_1_EFR___","OL_1_ERR___",
                             "SL_1_RBT___","OL_2_LFR___",
                             "OL_2_LRR___","SL_2_LST___",
                             "OL_2_WFR___","OL_2_WRR___",
                             "SL_2_WST___","SR_2_WAT___",
                             "SY_2_SYN___","SY_2_V10___",
                             "SY_2_VG1___","SY_2_VGP___"],
                'Sentinel-5 Precursor':["All S5P","L1B_IR_SIR","L1B_IR_UVN",
                                        "L1B_RA_BD1","L1B_RA_BD2","L1B_RA_BD3",
                                        "L1B_RA_BD4","L1B_RA_BD5",
                                        "L1B_RA_BD6","L1B_RA_BD7","L1B_RA_BD8",
                                        "L2__AER_AI","L2__CH4___","L2__CLOUD_",
                                        "L2__SO2___","L2__CO____","L2__HCHO__",
                                        "L2__NO2___","L2__O3____","L2__O3_TCL"],
               'Envisat':["ASA_IM__0P","ASA_WS__0P"],
               'Landsat-*':["L1TP"],
#                'Copernicus-Land':["All CLand"],
#                'Copernicus-Marine':["All CMarine"],
#                'Copernicus-Atmosphere':["All Cams"]
              }
    m = widgets.Select(options=options)
    return m

def types(input):
    t = widgets.Dropdown(
        options=input,
        description='Type:',
        layout=Layout(width="30%"),
        disabled=False)
    return t

def ptypes(choice):
    t = widgets.Dropdown(
        options=choice,
        description='Product type:',
        layout=Layout(width="30%"),
        disabled=False,
    )
    return t

def get_key(miss, val): 
    for key, value in zip(miss.options.keys(),miss.options.values()): 
         if val in value: 
            return key 

def save_mp(data):
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"m.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def save_s(data):
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"sen.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def save_aoi(geo_json):
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"polygon.json")
    with open(file, 'w') as fp:
            json.dump(geo_json["geometry"], fp)
            print("\nSelection saved")

def read_aoi():
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"polygon.json")
    with open(file, 'r') as fp:
        polysel = json.load(fp)
    return polysel

def read_sen():
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"sen.log")
    with open(file, 'r') as fp:
        s = json.load(fp)
    return s

def read_mp():
    dest = os.path.abspath(os.path.join("modules", '..', 'outputs'))
    file = os.path.join(dest,"m.log")
    with open(file, 'r') as fp:
        mp = json.load(fp)
    return mp

def sensing_range(start,stop):
    # start e stop vengono dal widget
    if np.logical_or(start==None,stop==None) == True:
        return None
    else:
        return ["["+str(start)+"T00:00:00.000Z%20TO%20"+str(stop)+"T23:59:59.999Z"+"]","["+str(start)+"T00:00:00.000Z%20TO%20"+str(stop)+"T23:59:59.999Z"+"]"]

def _filters_():
    # sensing range
    sensing_start, sensing_stop = sensing()
    display(sensing_start)
    display(sensing_stop)
    btn = widgets.Button(description="Submit sensing range")
    display(btn)    
    def inputs(b):  
        print("Sensing range from %s to %s"%(sensing_start.value,sensing_stop.value))
        sens = sensing_range(sensing_start.value,sensing_stop.value)
        save_s(sens)
    btn.on_click(inputs)
    # mission and ptype
    miss = mission()
    display(miss)
#    ptype = widgets.Label()
    btn_p = widgets.Button(description="Submit mission")
    display(btn_p) 
    output_btn = widgets.Output()
    @output_btn.capture()
    def inputs_p(b):  
#        ptype.val = miss.value
        p = ptypes(miss.value)
        display(p)
        button = widgets.Button(description="Submit product type")
        display(button)
        def inp(b):
            print("Mission: %s && Product Type: %s"%(get_key(miss, p.value),p.value))
            save_mp([get_key(miss, p.value),p.value])
        button.on_click(inp)

    btn_p.on_click(inputs_p)
    display(output_btn)


