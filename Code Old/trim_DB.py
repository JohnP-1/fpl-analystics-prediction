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


# data_old = data[data['season']!=2020].reset_index(drop=True)
data = data[data['season']!=2020].reset_index(drop=True)
# data_new = data[data['season']==2020]
#
# data_new = data_new[data_new['round']<=18].reset_index(drop=True)
#
# data = pd.concat([data_old, data_new], axis=0).reset_index(drop=True)

data.to_csv(path.join(path_processed, filename_player_database), index=False)
