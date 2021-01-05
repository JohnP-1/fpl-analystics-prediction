import DataLoaderHistoric as DLH
import pandas as pd
import os.path as path

###### Create DataLoader object ######

DataLoader = DLH.DataLoaderHistoric()

year = 2019

print('Processing Team Information')
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
