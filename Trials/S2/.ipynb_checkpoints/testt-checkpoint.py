import data_processing_S2 as dp
import time

st = time.time()

#rgb = dp.image(dp.open_rgb_bands("/mnt/Copernicus/OPTICAL/LEVEL-2A/2019/12/31/S2A_MSIL2A_20191231T000241_N0213_R030_T56HKF_20191231T015159.zip"))
rgb_snow = dp.image(dp.open_rgb_snow("/mnt/Copernicus/OPTICAL/LEVEL-2A/2019/12/15/S2A_MSIL2A_20191215T110441_N0213_R094_T30SVG_20191215T122756.zip"))
print(time.time()-st)
