import pandas as pd
import os.path as path

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_player_database = 'player_database.csv'
filename_player_database_historic = 'player_database_historic.csv'


data = pd.read_csv(path.join(path_processed, filename_player_database))
data_historic = pd.read_csv(path.join(path_processed, filename_player_database_historic))

data = data[data['season']==2020]
print(data.shape, data_historic.shape)

data = pd.concat([data_historic, data], axis=0)
data = data.reset_index(drop='index')
print(data.shape)
data = data.drop_duplicates()
print(data.shape)
data.to_csv(path.join(path_processed, filename_player_database), index=False)
