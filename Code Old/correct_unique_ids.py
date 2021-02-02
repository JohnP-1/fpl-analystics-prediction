import DataLoaderHistoric as DLH
import pandas as pd
import os.path as path
import DataLoader as DL
import os.path as path
import random
import numpy as np

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_modelling_db = 'test_database.csv'
filename_player_database = 'player_database.csv'
filename_player_metadata = 'player_metadata.csv'
filename_team_metadata = 'team_metadata.csv'

data = pd.read_csv(path.join(path_processed, filename_player_database))
player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))

I = data.shape[0]

for i in range(data.shape[0]):

    if ((i / I) * 100) % 1 == 0:
        print('Processed ', str((i / I) * 100), '%')
    player_name = data['name'].iloc[i]
    season = data['season'].iloc[i]

    unique_id = player_metadata[(player_metadata['name']==player_name) & (player_metadata['season']==season)]['unique_id'].values
    print(player_name, season)
    print('unique_id = ', unique_id)

    data['unique_id'].iloc[i] = unique_id

data = data.reset_index(drop=True)
data = data.drop_duplicates()

data.to_csv(path.join(path_processed, filename_player_database), index=False)
