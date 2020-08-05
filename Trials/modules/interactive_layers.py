import os, sys
sys.path.append(os.path.join(os.path.expanduser("~"),"CLEOPE/Trials/modules"))
import aoi, buttons
from ipywidgets import interact

df = aoi.read_query()
polysel,item,sensing = buttons.read_selections()

@interact
def _iFP_(product=[f for f in df.iloc[:,1]]): 
    keys = df.index[df['name'] == product].tolist()
    m = aoi.update_Map(keys,polysel,df)
    display(m)
    display(df.loc[keys])
    aoi.warning(df.loc[keys].iloc[:,6].any())
    print("Find item using ENS at pseudopath:\n%s"%os.path.join(str(df.loc[keys].iloc[:,2].any()),str(df.loc[keys].iloc[:,1].any())))
 
# allows to save up selections ready for download 
print("\nSelect products & save them to file.\nMultiple values can be selected with shift and/or ctrl (or cmd) pressed and mouse clicks!")
sel = buttons.select_product(df)
sel.display_widgets()
