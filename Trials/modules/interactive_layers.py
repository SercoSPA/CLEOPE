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
