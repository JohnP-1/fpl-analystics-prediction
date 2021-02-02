import DataLoaderHistoric as DLH
import pandas as pd
import os.path as path

###### Create DataLoader object ######

DataLoader = DLH.DataLoaderHistoric()

year = 2016

print('Processing Team Information')
for gw in range(1, 39):
    file_GW = 'gw' + str(gw) + '.csv'
    data_gw = DataLoader.load_gw(path.join(DataLoader.path_data_season(year), 'gws', file_GW), encoding='ISO 8859-1')
    DataLoader.save_gw(data_gw, path.join(DataLoader.path_data_season(year), 'gws', file_GW), encoding='UTF-8')

for gw in range(1, 39):
    DataLoader.process_player_teams(year, gw)

print('Processing League Standings')
for gw in range(1, 39):
    DataLoader.process_league_standings(year, gw)

print('Processing Next Fixtures')
for gw in range(1, 39):
    DataLoader.process_fixtures(year, gw)

print('Processing Player Names')
for gw in range(1, 39):
    DataLoader.process_playernames(year, gw)

print('Processing Player Position')
for gw in range(1, 39):
    DataLoader.add_position(gw, year)
