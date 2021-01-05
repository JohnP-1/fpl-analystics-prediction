import DataLoader as DL
import os.path as path

###### File Paths ######
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
filename_modelling_db = 'model_database.csv'
filename_player_database = 'player_database.csv'
filename_player_metadata = 'player_metadata.csv'
filename_team_metadata = 'team_metadata.csv'

DataLoaderObj = DL.DataLoader()
DataLoaderObj.process_database_model(path_processed,
                               filename_modelling_db,
                               filename_player_database,
                               filename_player_metadata,
                               filename_team_metadata)
