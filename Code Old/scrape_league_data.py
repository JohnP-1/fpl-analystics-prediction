import DataLoader as DL
import os.path as path

season = 2020

path_league_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_standings_full.csv')
path_league_data_full = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_data_full.csv')

DataLoaderObj = DL.DataLoader()
DataLoaderObj.scrape_league_standings(path_league_data_full,
                                      path_league_data,
                                      league_id=1217918,
                                      league_type='classic')
