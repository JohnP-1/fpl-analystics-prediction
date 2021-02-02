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

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_player_database = 'test_database.csv'
filename_player_metadata = 'player_metadata.csv'
filename_team_metadata = 'team_metadata.csv'

###### Parameters ######


###### Create DataLoader object ######

DataLoader = DLH.DataLoaderHistoric()

seasons = [2016,
           2017,
           2018,
           2019]

# print("Processing the team metadata")
# DataLoader.process_team_metadata(path_processed,
#                                  filename_team_metadata,
#                                  seasons)
#
# gws = list(range(1, 39))
#
# print("Processing the player metadata")
# DataLoader.process_player_metadata(path_processed,
#                                    filename_player_metadata,
#                                    filename_team_metadata,
#                                    seasons,
#                                    gws)
#
# print("Processing the player database")
# DataLoader.process_player_database_vis(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         seasons,
#                                         gws)

stat_columns = ['assists',
              'bonus',
              'bps',
              'clean_sheets',
              'creativity',
              'goals_conceded',
              'goals_scored',
              'ict_index',
              'influence',
              'minutes',
              'own_goals',
              'penalties_missed',
              'penalties_saved',
              'red_cards',
              'saves',
              'selected',
              'threat',
              'total_points',
              'transfers_balance',
              'value',
              'yellow_cards']

# stat_columns = ['goals_scored']


print("Processing the aggregate features")
DataLoader.calculate_aggregate_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=None)

DataLoader.calculate_aggregate_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=True)

DataLoader.calculate_aggregate_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=False)

print("Processing the stat features")
DataLoader.calculate_stat_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=None)

DataLoader.calculate_stat_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=True)

DataLoader.calculate_stat_features(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        home=False)
#
print("Processing the rolling stat features, window size = 3")
DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            home=None)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            home=True)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            home=False)

print("Processing the rolling stat features, window size = 4")
DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            home=None)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            home=True)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            home=False)

print("Processing the rolling stat features, window size = 5")
DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            home=None)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            home=True)

DataLoader.calculate_statrolling_features(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            home=False)

print("Processing the prob greater than 0")
DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=0,
                                        home=None)

DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=0,
                                        home=True)

DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=0,
                                        home=False)

print("Processing the prob greater than 1")
DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=1,
                                        home=None)

DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=1,
                                        home=True)

DataLoader.calculate_prob_occur(path_processed,
                                        filename_player_database,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns=stat_columns,
                                        event=1,
                                        home=False)

print("Processing the prob greater than 0, window size = 3")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=False)

print("Processing the prob greater than 0, window size = 4")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=False)

print("Processing the prob greater than 0, window size = 5")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            event=0,
                                            home=False)


print("Processing the prob greater than 1, window size = 3")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=False)

print("Processing the prob greater than 1, window size = 4")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=4,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=False)

print("Processing the prob greater than 1, window size = 5")
DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=3,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=None)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=True)

DataLoader.calculate_prob_occur_rolling(path_processed,
                                            filename_player_database,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            window_size=5,
                                            target_columns=stat_columns,
                                            event=1,
                                            home=False)


