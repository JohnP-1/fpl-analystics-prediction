import DataLoaderHistoric as DLH
import pandas as pd
import os.path as path

DataLoader = DLH.DataLoaderHistoric()

years = [2016, 2017, 2018, 2019]

for year in years:
    for gw in range(1, 39):
        print(f'Process in gw {gw} in season {year}')
        DataLoader.add_position(gw, year)
