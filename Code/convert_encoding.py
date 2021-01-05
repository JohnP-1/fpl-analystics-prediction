import process_gw_data as pgw
import pandas as pd
import os.path as path

###### Create DataLoader object ######

DataLoader = pgw.DataLoader()

year = 2018

for gw in range(1, 39):
    print(gw)
    file_GW = 'gw' + str(gw) + '.csv'
    # print(path.join(DataLoader.path_data_season(2016), 'gws', file_GW))
    data_gw = DataLoader.load_gw(path.join(DataLoader.path_data_season(year), 'gws', file_GW), encoding='ISO 8859-1')
    # print(data_gw)
    DataLoader.save_gw(data_gw, path.join(DataLoader.path_data_season(year), 'gws', file_GW), encoding='UTF-8')
