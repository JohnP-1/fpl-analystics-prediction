import DataLoaderHistoric as DLH
import DataLoader as DL
import pandas as pd
import os.path as path

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_player_database = 'player_database.csv'
filename_player_metadata = 'player_metadata.csv'
filename_team_metadata = 'team_metadata.csv'

###### Parameters ######


###### Create DataLoader object ######

DataLoader = DLH.DataLoaderHistoric()
DataLoaderFixt = DL.DataLoader()
fixtures = DataLoaderFixt.scrape_fixtures()
fixtures.to_csv(path.join('/home/john/Documents/projects/fpl-analystics-prediction/Data/2020-21', 'fixtures.csv'), index=False)

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

# stat_columns = ['assists',
#               'bonus',
#               'bps',
#               'clean_sheets',
#               'creativity',
#               'goals_conceded',
#               'goals_scored',
#               'ict_index',
#               'influence',
#               'minutes',
#               'own_goals',
#               'penalties_missed',
#               'penalties_saved',
#               'red_cards',
#               'saves',
#               'selected',
#               'threat',
#               'total_points',
#               'transfers_balance',
#               'value',
#               'yellow_cards']

# stat_columns = ['goals_scored']


# print("Processing the aggregate features")
# DataLoader.calculate_aggregate_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=None)
#
# DataLoader.calculate_aggregate_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=True)
#
# DataLoader.calculate_aggregate_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=False)
#
# print("Processing the stat features")
# DataLoader.calculate_stat_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=None)
#
# DataLoader.calculate_stat_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=True)
#
# DataLoader.calculate_stat_features(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         home=False)
# #
# print("Processing the rolling stat features, window size = 3")
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             home=None)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             home=True)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             home=False)
#
# print("Processing the rolling stat features, window size = 4")
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             home=None)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             home=True)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             home=False)
#
# print("Processing the rolling stat features, window size = 5")
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             home=None)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             home=True)
#
# DataLoader.calculate_statrolling_features(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             home=False)
#
# print("Processing the prob greater than 0")
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=0,
#                                         home=None)
#
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=0,
#                                         home=True)
#
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=0,
#                                         home=False)
#
# print("Processing the prob greater than 1")
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=1,
#                                         home=None)
#
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=1,
#                                         home=True)
#
# DataLoader.calculate_prob_occur(path_processed,
#                                         filename_player_database,
#                                         filename_player_metadata,
#                                         filename_team_metadata,
#                                         target_columns=stat_columns,
#                                         event=1,
#                                         home=False)
#
# print("Processing the prob greater than 0, window size = 3")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=False)
#
# print("Processing the prob greater than 0, window size = 4")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=False)
#
# print("Processing the prob greater than 0, window size = 5")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             event=0,
#                                             home=False)
#
#
# print("Processing the prob greater than 1, window size = 3")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=False)
#
# print("Processing the prob greater than 1, window size = 4")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=4,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=False)
#
# print("Processing the prob greater than 1, window size = 5")
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=3,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=None)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=True)
#
# DataLoader.calculate_prob_occur_rolling(path_processed,
#                                             filename_player_database,
#                                             filename_player_metadata,
#                                             filename_team_metadata,
#                                             window_size=5,
#                                             target_columns=stat_columns,
#                                             event=1,
#                                             home=False)

seasons = [2016,
           2017,
           2018,
           2019,
           2020]

# seasons = [2020]

for season in seasons:
    DataLoader.process_fixtures_season(season, path_processed)

DataLoader.process_team_stats_init(seasons,
                                path_processed)

DataLoader.process_team_stats(seasons,
                            path_processed)

for season in seasons:
    DataLoader.process_fixture_odds(path_processed,
                                 'fixtures.csv',
                                 'team_stats.csv',
                                 season,
                                 results_window=3)
    DataLoader.process_fixture_odds(path_processed,
                                 'fixtures.csv',
                                 'team_stats.csv',
                                 season,
                                 results_window=4)
    DataLoader.process_fixture_odds(path_processed,
                                 'fixtures.csv',
                                 'team_stats.csv',
                                 season,
                                 results_window=5)
    DataLoader.process_fixture_odds(path_processed,
                                 'fixtures.csv',
                                 'team_stats.csv',
                                 season,
                                 results_window=10)
