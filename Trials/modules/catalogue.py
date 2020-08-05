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