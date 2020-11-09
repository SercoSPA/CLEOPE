# -*- coding: utf-8 -*-
"""
 * Data and Information access services (DIAS) ONDA - For Space data distribution. 
 *
 * This file is part of CLEOPE (Cloud Earth Observation Processing Environment) software sources.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 
@author: GCIPOLLETTA
"""
import os, sys, warnings
sys.path.append(os.path.join(os.path.expanduser("~"),"CLEOPE/Trials/modules"))
import aoi, buttons, qm
from ipywidgets import widgets

def handle_draw(self, action, geo_json):
    buttons.save_aoi(geo_json)

buttons._filters_()
m,dc = aoi.define_map()
dc.on_draw(handle_draw)
m.add_control(dc)
display(m)

def send():
    polysel,item,sensing = buttons.read_selections()
    n = aoi.count(polysel,item,sensing)
    df = aoi.search(n,polysel,item,sensing)
    if n > 0:
        display(df.hvplot.table(sortable=True, selectable=True))
        df.to_csv(os.path.join(buttons.dirName,"query.csv"))

from IPython.display import display
clb = widgets.Button(description="RUN!")
display(clb)
output_btn = widgets.Output()
@output_btn.capture()
def on_button_clicked(b):
    send()
clb.on_click(on_button_clicked)
display(output_btn)