import DataLoaderHistoric as DLH
import pandas as pd
import os.path as path
import DataLoader as DL
import os.path as path
import random
import numpy as np

random.seed(100)

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_modelling_db = 'test_database.csv'
filename_player_database = 'player_database.csv'
filename_player_metadata = 'player_metadata.csv'
filename_team_metadata = 'team_metadata.csv'

data = pd.read_csv(path.join(path_processed, filename_player_database))

unique_ids = data['unique_id'].unique()

unique_ids_list1 = []
unique_ids_list19 = []
unique_ids_list38 = []

for unique_id in unique_ids:
    length = data[data['unique_id']==unique_id].shape[0]
    if length == 1:
        unique_ids_list1.append(unique_id)
    if np.sum(data[data['unique_id']==unique_id]['ict_index']) > 10:
        if length == 19:
            unique_ids_list19.append(unique_id)
        elif length ==38:
            unique_ids_list38.append(unique_id)


unique_ids_list1 = random.sample(unique_ids_list1, 2)
unique_ids_list19 = random.sample(unique_ids_list19, 2)
unique_ids_list38 = random.sample(unique_ids_list38, 2)

list_test = unique_ids_list1 + unique_ids_list19 + unique_ids_list38

data_test_list = []

for unique_id in list_test:
    data_test_list.append(data[data['unique_id']==unique_id])

data_test = pd.concat(data_test_list, axis=0).reset_index(drop='index')

data_test.to_csv(path.join(path_processed, filename_modelling_db), index=False)
