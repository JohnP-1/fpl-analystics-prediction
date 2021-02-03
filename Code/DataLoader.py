import numpy as np
import pandas as pd
from os import path
import os
import requests
import DataLoaderHistoric as DLH


class DataLoader(DLH.DataLoaderHistoric):

    def __init__(self):
        super().__init__()
        pass

    def process_data(self, season, parse=True, scrape=True):

        season_name = str(season) + '-' + str(season+1)[-2:]
        self.create_season_folder(season_name)
        self.create_GW_log(season_name)
        gw_log = self.open_df(path.join(self.get_base_path(), 'Data', season_name, 'gw_log.csv'))

        if scrape is True:
            self.scrape_data(season, gw_log)
        if parse is True:
            self.parse_data(season, gw_log)


    def scrape_data(self, season, gw_log):

        season_name = str(season) + '-' + str(season+1)[-2:]

        gws = self.determine_GW()

        for gw in range(1, gws):
            print('gw' + str(gw))
            if gw_log.iloc[gw-1, 1] == False:
                dataframes = self.scrape_bootstrap_static()
                gw_data = self.scrape_gw_history(gw, season)
                fixtures = self.scrape_fixtures()

                gw_data.to_csv(path.join(self.get_base_path(), 'Data', season_name, 'gws', 'gw' + str(gw) + '.csv'), index=False)
                fixtures.to_csv(path.join(self.get_base_path(), 'Data', season_name, 'fixtures.csv'), index=False)
                dataframes['teams'].to_csv(path.join(self.get_base_path(), 'Data', season_name, 'teams.csv'), index=False)
                dataframes['elements'].to_csv(path.join(self.get_base_path(), 'Data', season_name, 'gws_raw', 'gw' + str(gw) + '.csv'), index=False)
                dataframes['element_types'].to_csv(path.join(self.get_base_path(), 'Data', season_name, 'element_types.csv'), index=False)
                dataframes['element_stats'].to_csv(path.join(self.get_base_path(), 'Data', season_name, 'element_stats.csv'), index=False)
                dataframes['events'].to_csv(path.join(self.get_base_path(), 'Data', season_name, 'events.csv'), index=False)
                gw_log.iloc[gw-1, 1] = True
                gw_log.to_csv(path.join(self.get_base_path(), 'Data', season_name, 'gw_log.csv'), index=False)


    def parse_data(self, season, gw_log):

        seasons = [season]
        season_name = str(season) + '-' + str(season+1)[-2:]

        path_processed = path.join(self.get_base_path(), 'Processed')
        filename_player_database = 'player_database.csv'
        filename_player_metadata = 'player_metadata.csv'
        filename_team_metadata = 'team_metadata.csv'

        target_columns = ['assists',
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

        # gw_curr = self.determine_GW()
        gws = self.determine_GW()

        for gw_curr in range(1, gws):
            if gw_log.iloc[gw_curr-1, 2] == False:

                print('Processing Team Information')
                self.add_position(gw_curr, season)

                print('Processing Team Information')
                self.process_player_teams(season, gw_curr)

                print('Processing League Standings')
                self.process_league_standings(season, gw_curr)

                print('Processing Next Fixtures')
                self.process_fixtures(season, gw_curr)

                print('Processing Player Names')
                self.process_playernames(season, gw_curr)

                self.process_team_metadata(path_processed,
                                      filename_team_metadata,
                                      seasons)

                print("Processing the player metadata")
                self.process_player_metadata(path_processed,
                                           filename_player_metadata,
                                           filename_team_metadata,
                                           seasons,
                                           [gw_curr])

                print("Processing the player database")
                player_database_gw = self.process_player_database_vis(path_processed,
                                                                    filename_player_database,
                                                                    filename_player_metadata,
                                                                    filename_team_metadata,
                                                                    seasons,
                                                                    [gw_curr])

                player_database_gw = self.combine_player_database(player_database_gw,
                                            path_processed,
                                            filename_player_database)

                filename_player_data = 'player_db_' + str(gw_curr) + '.csv'

                player_database_gw.to_csv(path.join(path_processed, filename_player_data), index=False)


                print("Processing the aggregate features")
                player_database_gw = self.calculate_aggregate_features(player_database_gw,
                                                                    path_processed,
                                                                    filename_player_database,
                                                                    filename_player_metadata,
                                                                    filename_team_metadata,
                                                                    season,
                                                                    target_columns,
                                                                    gw_curr,
                                                                    home=None)

                player_database_gw = self.calculate_aggregate_features(player_database_gw,
                                                                       path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns,
                                                gw_curr,
                                                home=True)

                player_database_gw = self.calculate_aggregate_features(player_database_gw,
                                                                       path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns,
                                                gw_curr,
                                                home=False)



                print("Processing the stat features")
                player_database_gw = self.calculate_stat_features(player_database_gw,
                                                                  path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns,
                                                gw_curr,
                                                home=None)

                player_database_gw = self.calculate_stat_features(player_database_gw,
                                                                  path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns,
                                                gw_curr,
                                                home=True)

                player_database_gw = self.calculate_stat_features(player_database_gw,
                                                                  path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns,
                                                gw_curr,
                                                home=False)

                print("Processing the rolling stat features, window size = 3")
                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                                         path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=3,
                                                    home=None)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                                         path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=3,
                                                    home=True)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                                         path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=3,
                                                    home=False)

                print("Processing the rolling stat features, window size = 4")
                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=4,
                                                    home=None)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=4,
                                                    home=True)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=4,
                                                    home=False)


                print("Processing the rolling stat features, window size = 5")
                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=5,
                                                    home=None)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=5,
                                                    home=True)

                player_database_gw = self.calculate_statrolling_features(player_database_gw,
                                                    path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    target_columns,
                                                    gw_curr,
                                                    window_size=5,
                                                    home=False)

                print("Processing the prob greater than 0")
                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=0,
                                                home=None)

                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=0,
                                                home=True)

                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=0,
                                                home=False)

                print("Processing the prob greater than 1")
                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=1,
                                                home=None)

                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=1,
                                                home=True)

                player_database_gw = self.calculate_prob_occur(player_database_gw,
                                          path_processed,
                                                filename_player_database,
                                                filename_player_metadata,
                                                filename_team_metadata,
                                                season,
                                                target_columns=target_columns,
                                                gw_curr=gw_curr,
                                                event=1,
                                                home=False)

                print("Processing the prob greater than 0, window size = 3")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=False)

                print("Processing the prob greater than 0, window size = 4")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=False)

                print("Processing the prob greater than 0, window size = 5")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=5,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=5,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=0,
                                                    home=False)


                print("Processing the prob greater than 1, window size = 3")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=False)

                print("Processing the prob greater than 1, window size = 4")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=4,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=False)

                print("Processing the prob greater than 1, window size = 5")
                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=3,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=None)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=5,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=True)

                player_database_gw = self.calculate_prob_occur_rolling(player_database_gw,
                                                  path_processed,
                                                    filename_player_database,
                                                    filename_player_metadata,
                                                    filename_team_metadata,
                                                    season,
                                                    window_size=5,
                                                    target_columns=target_columns,
                                                    gw_curr=gw_curr,
                                                    event=1,
                                                    home=False)


                player_database_gw.to_csv(path.join(path_processed, filename_player_database), index=False)

                gw_log.iloc[gw_curr-1, 2] = True
                gw_log.to_csv(path.join(self.get_base_path(), 'Data', season_name, 'gw_log.csv'), index=False)


    def get_base_path(self):
        
        return path.dirname(path.dirname(__file__))


    def create_season_folder(self, season_name):

        path_season = path.join(self.get_base_path(), 'Data', season_name)

        if self.check_folder_exists(path_season) is False:
            os.mkdir(path_season)
            os.mkdir(path.join(path_season, 'gws'))
            os.mkdir(path.join(path_season, 'gws_raw'))
        else:
            print('season folder found')


    def check_file_exists(self, file_path):
        """
        Checks if a file exists.

        :param file_path: Str --> Path to file
        :return: Bool
        """
        return path.exists(file_path)


    def check_folder_exists(self, folder_path):
        """
        Checks if a file exists.

        :param file_path: Str --> Path to file
        :return: Bool
        """
        return path.exists(folder_path)
    

    def create_GW_log(self, season_name):

        path_file = path.join(self.get_base_path(), 'Data', season_name, 'gw_log.csv')
        
        if self.check_file_exists(path_file) is False:
            gw_log_data = {}
            gw_log_data['gw'] = range(1,39)
            gw_log_data['scraped'] = [False] * 38
            gw_log_data['parsed'] = [False] * 38
            gw_log = pd.DataFrame(gw_log_data)
            gw_log.to_csv(path_file, index=False)
        else:
            print('gw_log found')


    def open_df(self, file_path):

        if self.check_file_exists(file_path) is True:
            return pd.read_csv(file_path)
        else:
            return None

            
    def determine_GW(self):
        url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        r = requests.get(url)
        json = r.json()
        data = pd.DataFrame(json['events'])
        data = data[data['finished']==False].sort_values('id')['id']
        # print(data)

        if data.shape[0] > 0:
            return data.iloc[0]
        else:
            return -1


    def scrape_bootstrap_static(self, keys=['events','phases', 'teams', 'elements', 'element_stats', 'element_types']):

        url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
        r = requests.get(url)
        json = r.json()
        dataframes = {}

        for key in keys:
            dataframes[key] = pd.DataFrame(json[key])

        return dataframes


    def scrape_event(self, gw):


        elements = []

        url = 'https://fantasy.premierleague.com/api/event/' + str(gw) + '/live/'
        r = requests.get(url)
        json = r.json()
        json_elements = json['elements']


        for element in json_elements:
            elements.append(element['stats'])

        return pd.DataFrame(elements)


    def scrape_gw_history(self, gw, season, element_no=None):

        elements = []
        if element_no is None:
            element_no = 1
            element_flag = True
            while element_flag is True:
                # print(element_no)
                url = 'https://fantasy.premierleague.com/api/element-summary/' + str(element_no) + '/'
                r = requests.get(url)
                json = r.json()
                if json[list(json.keys())[0]] == 'Not found.':
                    element_flag = False
                else:
                    # Note the GW start at 0 for this API and there for will be offset by -1
                    # print(len(json['history']))
                    for i in range(len(json['history'])):
                        if json['history'][i]['round'] == gw:
                            elements.append(json['history'][i])
                    element_no += 1

        else:
            url = 'https://fantasy.premierleague.com/api/element-summary/' + str(element_no) + '/'
            r = requests.get(url)
            json = r.json()
            elements.append(json['history'][gw-1])

        gw_data = pd.DataFrame(elements)
        gw_data = gw_data.reindex(sorted(gw_data.columns), axis=1)

        dataframes = self.scrape_bootstrap_static()
        metadata = dataframes['elements'][['id', 'first_name', 'second_name']]
        metadata = metadata.rename(columns={'id': 'element'})
        metadata['name'] = metadata['first_name'] + '_' +  metadata['second_name']
        # metadata = metadata.drop(['first_name', 'second_name'], axis=1)
        gw_data = gw_data.merge(metadata, on=['element'])
        gw_data = gw_data.rename(columns={'first_name': 'name_first', 'second_name': 'name_last'})
        gw_data['season'] = season

        return gw_data


    def scrape_fixtures(self):

        url = 'https://fantasy.premierleague.com/api/fixtures/'
        r = requests.get(url)
        json = r.json()
        fixtures = pd.DataFrame(json)

        return fixtures


    def add_position(self, gw, year):

        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
        file_GW_raw = path.join('gws_raw', file_GW)
        data_player_raw = self.load_raw_player_data(path.join(self.path_data_season(year), file_GW_raw))

        data_player_raw = data_player_raw[['id', 'element_type']]
        data_player_raw = data_player_raw.rename(columns={"id": "element"})

        data_gw = data_gw.merge(data_player_raw, on='element')
        print(list(data_gw.columns))
        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', file_GW), encoding='UTF-8', index=False)


    def process_fixtures(self, year,
                         gw):

        season_name = str(year) + '-' + str(year+1)[-2:]
        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))

        data_gw['next_fixture_team'] = 0
        data_gw['next_fixture_position'] = 0
        data_gw['next_fixture_points'] = 0
        data_gw['next_fixture_wins'] = 0
        data_gw['next_fixture_draws'] = 0
        data_gw['next_fixture_losses'] = 0
        data_gw['next_fixture_goals_for'] = 0
        data_gw['next_fixture_goals_against'] = 0
        data_gw['next_fixture_goals_diff'] = 0
        data_gw['next_fixture_played'] = 0
        data_gw['next_fixture_yc'] = 0
        data_gw['next_fixture_rc'] = 0

        fixtures = pd.read_csv(path.join(self.get_base_path(), 'Data', season_name, 'fixtures.csv'))

        for i in range(data_gw.shape[0]):
            player = data_gw['element'].iloc[i]
            team_player = data_gw['team'].iloc[i]

            gw_next = gw + 1
            fixtures_next = fixtures[fixtures['event']==gw_next]

            if gw_next < 38:
                file_league_table_curr = 'league_table_gw' + str(gw) + '.csv'
                teams_next = self.load_gw(path.join(self.path_data_season(year), 'gws', file_league_table_curr))

            for j in range(fixtures_next.shape[0]):
                if fixtures_next['team_h'].iloc[j] == team_player:
                    team = fixtures_next['team_a'].iloc[j]
                elif fixtures_next['team_a'].iloc[j] == team_player:
                    team = fixtures_next['team_h'].iloc[j]

            data_gw['next_fixture_team'][data_gw['element']==player] = team
            data_gw['next_fixture_position'][data_gw['element']==player] = teams_next[teams_next['id']==team]['position'].values[0]
            data_gw['next_fixture_points'][data_gw['element']==player] = teams_next[teams_next['id']==team]['points'].values[0]
            data_gw['next_fixture_wins'][data_gw['element']==player] =teams_next[teams_next['id']==team]['wins'].values[0]
            data_gw['next_fixture_draws'][data_gw['element']==player] = teams_next[teams_next['id']==team]['draws'].values[0]
            data_gw['next_fixture_losses'][data_gw['element']==player] = teams_next[teams_next['id']==team]['losses'].values[0]
            data_gw['next_fixture_goals_for'][data_gw['element']==player] = teams_next[teams_next['id']==team]['goals_for'].values[0]
            data_gw['next_fixture_goals_against'][data_gw['element']==player] = teams_next[teams_next['id']==team]['goals_against'].values[0]
            data_gw['next_fixture_goals_diff'][data_gw['element']==player] = teams_next[teams_next['id']==team]['goals_diff'].values[0]
            data_gw['next_fixture_played'][data_gw['element']==player] = teams_next[teams_next['id']==team]['played'].values[0]
            data_gw['next_fixture_yc'][data_gw['element']==player] = teams_next[teams_next['id']==team]['yc'].values[0]
            data_gw['next_fixture_rc'][data_gw['element']==player] = teams_next[teams_next['id']==team]['rc'].values[0]

        data_GW = 'gw' + str(gw) + '.csv'
        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', data_GW), encoding='UTF-8', index=False)


    def process_player_teams(self, year,
                             gw):
        """
        Function used to label a the team a specific player plays for. This team label is the team ID used for a specific season, not the unique team ID created later.

        :param year: Int --> Year of season to be selected
        :param gw: Int --> Game week
        :return: None
        """

        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
        data_player_raw = self.load_raw_player_data(path.join(self.path_data_season(year), 'gws_raw', file_GW))

        data_gw['team'] = np.zeros(data_gw.shape[0])

        for i in range(data_gw.shape[0]):
            player_id = data_gw['element'].iloc[i]
            player_team = data_player_raw[data_player_raw['id']==player_id]['team']
            data_gw['team'].iloc[i] = int(player_team.values)

        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', file_GW), encoding='UTF-8', index=False)


    def process_player_database_vis(self, path_processed,
                                    filename_player_data,
                                    filename_player_metadata,
                                    filename_team_metadata,
                                    seasons,
                                    gws):
        """
        Function used to create the final player for visualisation purposes. This reads in each player from each gameweek. it also assigns the player and team the unique ID as specified in the player and team metadata files. This allows for the same player to be treated as different entities between season
        :param path_processed:
        :param filename_player_data:
        :param filename_player_metadata:
        :param filename_team_metadata:
        :param seasons:
        :param gws:
        :return:
        """

        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # self.create_player_data(path_processed, filename_player_data)
        # player_data = pd.read_csv(path.join(path_processed, filename_player_data))

        columns = ['unique_id',
                  'season',
                  'name',
                  'assists',
                  'bonus',
                  'bps',
                  'clean_sheets',
                  'creativity',
                  'element',
                  'element_type',
                  'fixture',
                  'goals_conceded',
                  'goals_scored',
                  'ict_index',
                  'influence',
                  'kickoff_time',
                  'minutes',
                  'own_goals',
                  'penalties_missed',
                  'penalties_saved',
                  'red_cards',
                  'round',
                  'saves',
                  'selected',
                  'team_a_score',
                  'team_h_score',
                  'threat',
                  'total_points',
                  'transfers_balance',
                  'transfers_in',
                  'transfers_out',
                  'value',
                  'was_home',
                  'yellow_cards',
                  'position',
                  'team_unique_id',
                  'team_id',
                  'team_name',
                  'team_points',
                  'team_wins',
                  'team_draws',
                  'team_losses',
                  'team_goals_for',
                  'team_goals_against',
                  'team_goals_diff',
                  'team_played',
                  'team_yc',
                  'team_rc',
                  'team_position',
                  'next_fixture_team',
                  'next_fixture_position',
                  'next_fixture_points',
                  'next_fixture_wins',
                  'next_fixture_draws',
                  'next_fixture_losses',
                  'next_fixture_goals_for',
                  'next_fixture_goals_against',
                  'next_fixture_goals_diff',
                  'next_fixture_played',
                  'next_fixture_yc',
                  'next_fixture_rc']


        player_data = pd.DataFrame([], columns=columns)

        #Loop through every season
        for year in seasons:
            #Loop through every gameweek.
            for gw in gws:
                print(f'Processing GW {gw} of season {year}')
                file_GW = 'gw' + str(gw) + '.csv'
                data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
                data_gw = data_gw.rename(columns={"team": "team_id"})
                for i in range(data_gw.shape[0]):
                    name = data_gw['name'].iloc[i].split('_')
                    if len(name) > 2:
                        name = name[0] + '_' + name[1]
                        data_gw['name'].iloc[i] = name

                print(data_gw)
                print(list(data_gw.columns))
                player_data_temp = data_gw.merge(player_metadata, on=['name', 'season', 'name_first', 'name_last', 'team_id', 'element_type'])
                player_data_temp = player_data_temp.rename(columns={"team": "team_id"})
                file_league = 'league_table_gw' + str(gw) + '.csv'
                data_league = self.load_gw(path.join(self.path_data_season(year), 'gws', file_league))
                data_league = data_league.rename(columns={"id": "team_id",
                                                          "name": "team_name",
                                                          "points": "team_points",
                                                          "wins": "team_wins",
                                                          "draws": "team_draws",
                                                          "losses": "team_losses",
                                                          "goals_for": "team_goals_for",
                                                          "goals_against": "team_goals_against",
                                                          "goals_diff": "team_goals_diff",
                                                          "played": "team_played",
                                                          "yc": "team_yc",
                                                          "rc": "team_rc",
                                                          "position": "team_position"})

                player_data_temp = player_data_temp.merge(data_league, on=['team_id'])
                player_data_temp = player_data_temp.merge(team_metadata, on=['team_id', 'season', 'team_name', 'team_unique_id'])
                # print(player_data_temp)
                player_data_temp['next_fixture_team_unique_id'] = 0
                for i in range(player_data_temp.shape[0]):
                    player_team = player_data_temp.iloc[i, :]
                    if player_team['next_fixture_team'] != 0:
                        player_team = player_team[['season', 'next_fixture_team']]
                        player_team = pd.DataFrame(data = [player_team.values], columns = player_team.index)
                        player_team = player_team.rename(columns={"next_fixture_team": "team_id"})
                        player_team = player_team.merge(team_metadata, on=['season', 'team_id'])
                        unique_id = player_team['team_unique_id']

                        player_data_temp['next_fixture_team_unique_id'][i] = unique_id

                player_data_temp = player_data_temp[player_data.columns]

                player_data = pd.concat([player_data, player_data_temp])
                player_data = player_data.drop_duplicates()
                player_data = player_data.reset_index(level=0, drop=True)

        return player_data


    def get_team_id(self, player_metadata, unique_id):

        return player_metadata[player_metadata['unique_id']==unique_id]['team_id'].values[0]


    def check_unique_id_played(self,
                               player_metadata,
                               gw_curr,
                               season,
                               unique_id):

        season_name = str(season) + '-' + str(season+1)[-2:]
        fixture_data = pd.read_csv(path.join(self.get_base_path(), 'Data', season_name, 'fixtures.csv'))
        fixture_data = fixture_data[fixture_data['event']==gw_curr]

        team_id = self.get_team_id(player_metadata, unique_id)

        team_played = False

        # print(team_id)
        # print(fixture_data['team_h'])

        if team_id in fixture_data['team_h'].values:
            team_played = True

        if team_id in fixture_data['team_a'].values:
            team_played = True

        if team_played is False:
            print(team_id, gw_curr)

        return team_played



    def calculate_aggregate_features(self, player_data,
                                        path_processed,
                                        filename_player_data,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        season,
                                        target_columns,
                                        gw_curr,
                                        home=None):

        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # try:
        #     player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        # except:
        #     print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data_old = player_data[player_data['season']!=season].copy()
        player_data_old_season = player_data[(player_data['season']==season) & (player_data['round']!=gw_curr)]
        player_data_old = pd.concat([player_data_old, player_data_old_season], axis=0).reset_index(drop=True)

        player_data_season = player_data[player_data['season']==season]
        player_data = player_data[(player_data['season']==season) & (player_data['round']==gw_curr)]

        target_column_agg_list = []
        for target_column in target_columns:
            # Add placeholder for the aggregate features
            if home is None:
                target_column_agg = 'total_' + target_column + '_any_all'
            elif home is True:
                target_column_agg = 'total_' + target_column + '_home_all'
            elif home is False:
                target_column_agg = 'total_' + target_column + '_away_all'
            target_column_agg_list.append(target_column_agg)
            player_data[target_column_agg] = 0

        # Create new empty player_database with the same columns, the unique DataFrame with aggreage features will be added to this.
        # player_data_aggregate = pd.DataFrame([], columns=player_data.columns)
        player_data_aggregate = []

        # Find the list of unique_ids in the DataFrame
        unique_ids = pd.unique(player_data.sort_values('unique_id')['unique_id'])

        for unique_id in unique_ids:

            if unique_id % 100 == 0:
                print(f"Processing unique_id {unique_id} of {unique_ids[-1]}")

            # Filter the DataFrame to return a DataFrame for every unique player id and then sort on the round.
            player_data_unique_id = player_data_season[player_data_season['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)
            player_data_unique_id_gw = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # Iterate through the sorted dataframe to calculate the aggregate features
            if home is None:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = np.sum(player_data_unique_id[target_columns].values, axis=0)
            elif home is True:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==True]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = np.sum(player_data_unique_id_temp[target_columns].values, axis=0)

            elif home is False:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==False]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = np.sum(player_data_unique_id_temp[target_columns].values, axis=0)
            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id_gw)

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = pd.concat([player_data_old, player_data_aggregate])
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        # player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data_aggregate


    def calculate_stat_features(self, player_data,
                                path_processed,
                                filename_player_data,
                                filename_player_metadata,
                                filename_team_metadata,
                                season,
                                target_columns,
                                gw_curr,
                                home=None):


        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # try:
        #     player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        # except:
        #     print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data_old = player_data[player_data['season']!=season].copy()
        player_data_old_season = player_data[(player_data['season']==season) & (player_data['round']!=gw_curr)]
        player_data_old = pd.concat([player_data_old, player_data_old_season], axis=0).reset_index(drop=True)

        player_data_season = player_data[player_data['season']==season]
        player_data = player_data[(player_data['season']==season) & (player_data['round']==gw_curr)]

        target_column_mean_list = []
        target_column_median_list = []
        target_column_std_list = []
        target_column_se_list = []
        target_column_range_list = []
        for target_column in target_columns:

            if home is None:
                target_column_mean = 'mean_' + target_column + '_any_all'
                target_column_median = 'median_' + target_column + '_any_all'
                target_column_std = 'std_' + target_column + '_any_all'
                target_column_se = 'se_' + target_column + '_any_all'
                target_column_range = 'range_' + target_column + '_any_all'
            elif home is True:
                target_column_mean = 'mean_' + target_column + '_home_all'
                target_column_median = 'median_' + target_column + '_home_all'
                target_column_std = 'std_' + target_column + '_home_all'
                target_column_se = 'se_' + target_column + '_home_all'
                target_column_range = 'range_' + target_column + '_home_all'
            elif home is False:
                target_column_mean = 'mean_' + target_column + '_away_all'
                target_column_median = 'median_' + target_column + '_away_all'
                target_column_std = 'std_' + target_column + '_away_all'
                target_column_se = 'se_' + target_column + '_away_all'
                target_column_range = 'range_' + target_column + '_away_all'

            # Add placeholder for the stat features
            player_data[target_column_mean] = 0
            player_data[target_column_median] = 0
            player_data[target_column_std] = 0
            player_data[target_column_se] = 0
            player_data[target_column_range] = 0

            target_column_mean_list.append(target_column_mean)
            target_column_median_list.append(target_column_median)
            target_column_std_list.append(target_column_std)
            target_column_se_list.append(target_column_se)
            target_column_range_list.append(target_column_range)


        # Create new empty player_database with the same columns, the unique DataFrame with aggreage features will be added to this.
        player_data_aggregate = []

        # Find the list of unique_ids in the DataFrame
        unique_ids = pd.unique(player_data.sort_values('unique_id')['unique_id'])

        for unique_id in unique_ids:

            if unique_id % 100 == 0:
                print(f"Processing unique_id {unique_id} of {unique_ids[-1]}")

            # Filter the DataFrame to return a DataFrame for every unique player id and then sort on the round.
            player_data_unique_id = player_data_season[player_data_season['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)
            player_data_unique_id_gw = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # Iterate through the sorted dataframe to calulate the aggregate features
            if home is None:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id[target_columns].values, axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id[target_columns].values, axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id[target_columns].values, dtype=np.float64), axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id[target_columns].shape[0])
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id[target_columns].values, axis=0) - np.min(player_data_unique_id[target_columns].values, axis=0)
            elif home is True:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==True]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

            elif home is False:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==False]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)


            player_data_aggregate.append(player_data_unique_id_gw)

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = pd.concat([player_data_old, player_data_aggregate])
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        # player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data_aggregate


    def calculate_statrolling_features(self, player_data,
                                        path_processed,
                                        filename_player_data,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        season,
                                        target_columns,
                                        gw_curr,
                                        window_size=3,
                                        home=None):

        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # try:
        #     player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        # except:
        #     print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data_old = player_data[player_data['season']!=season].copy()
        player_data_old_season = player_data[(player_data['season']==season) & (player_data['round']!=gw_curr)]
        player_data_old = pd.concat([player_data_old, player_data_old_season], axis=0).reset_index(drop=True)

        player_data_season = player_data[player_data['season']==season]
        player_data = player_data[(player_data['season']==season) & (player_data['round']==gw_curr)]

        target_column_mean_list = []
        target_column_median_list = []
        target_column_std_list = []
        target_column_se_list = []
        target_column_range_list = []
        for target_column in target_columns:
            if home is None:
                target_column_mean = 'mean_' + target_column + '_any_' + str(window_size)
                target_column_median = 'median_' + target_column + '_any_' + str(window_size)
                target_column_std = 'std_' + target_column + '_any_' + str(window_size)
                target_column_se = 'se_' + target_column + '_any_' + str(window_size)
                target_column_range = 'range_' + target_column + '_any_' + str(window_size)
            elif home is True:
                target_column_mean = 'mean_' + target_column + '_home_' + str(window_size)
                target_column_median = 'median_' + target_column + '_home_' + str(window_size)
                target_column_std = 'std_' + target_column + '_home_' + str(window_size)
                target_column_se = 'se_' + target_column + '_home_' + str(window_size)
                target_column_range = 'range_' + target_column + '_home_' + str(window_size)
            elif home is False:
                target_column_mean = 'mean_' + target_column + '_away_' + str(window_size)
                target_column_median = 'median_' + target_column + '_away_' + str(window_size)
                target_column_std = 'std_' + target_column + '_away_' + str(window_size)
                target_column_se = 'se_' + target_column + '_away_' + str(window_size)
                target_column_range = 'range_' + target_column + '_away_' + str(window_size)

            # Add placeholder for the stat features
            player_data[target_column_mean] = 0
            player_data[target_column_median] = 0
            player_data[target_column_std] = 0
            player_data[target_column_se] = 0
            player_data[target_column_range] = 0

            target_column_mean_list.append(target_column_mean)
            target_column_median_list.append(target_column_median)
            target_column_std_list.append(target_column_std)
            target_column_se_list.append(target_column_se)
            target_column_range_list.append(target_column_range)

        # Create new empty player_database with the same columns, the unique DataFrame with aggregate features will be added to this.
        player_data_aggregate = []

        # Find the list of unique_ids in the DataFrame
        unique_ids = pd.unique(player_data.sort_values('unique_id')['unique_id'])

        for unique_id in unique_ids:

            if unique_id % 100 == 0:
                print(f"Processing unique_id {unique_id} of {unique_ids[-1]}")

            # Filter the DataFrame to return a DataFrame for every unique player id and then sort on the round.
            player_data_unique_id = player_data_season[player_data_season['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)
            player_data_unique_id_gw = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # if player_data_unique_id.shape[0] > 0:
            I = player_data_unique_id.shape[0]
            offset = window_size - 1

            if home is None:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id.iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)

            if home is True:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id[player_data_unique_id['was_home']==True].iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)

            elif home is False:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id[player_data_unique_id['was_home']==False].iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)


            if home is None:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, dtype=np.float64), axis=0)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, dtype=np.float64), axis=0)/np.sqrt(window_size)
                    player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, axis=0) - np.min(player_data_unique_id.loc[player_data_unique_id.index[-window_size:], target_columns].values, axis=0)
            elif home is True:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==True].iloc[-window_size:, :]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

            elif home is False:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==False].iloc[-window_size:, :]
                    if player_data_unique_id_temp.shape[0] == 0:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = 0
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = 0
                    else:
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id_gw)

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = pd.concat([player_data_old, player_data_aggregate])
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        # player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data_aggregate


    def calculate_prob_occur(self, player_data,
                                    path_processed,
                                    filename_player_data,
                                    filename_player_metadata,
                                    filename_team_metadata,
                                    season,
                                    target_columns,
                                    gw_curr,
                                    event=0,
                                    home=None):


        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # try:
        #     player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        # except:
        #     print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data_old = player_data[player_data['season']!=season].copy()
        player_data_old_season = player_data[(player_data['season']==season) & (player_data['round']!=gw_curr)]
        player_data_old = pd.concat([player_data_old, player_data_old_season], axis=0).reset_index(drop=True)

        player_data_season = player_data[player_data['season']==season]
        player_data = player_data[(player_data['season']==season) & (player_data['round']==gw_curr)]

        target_column_agg_list = []
        for target_column in target_columns:
            # Add placeholder for the aggregate features
            if home is None:
                target_column_agg = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_any_all'
            elif home is True:
                target_column_agg = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_home_all'
            elif home is False:
                target_column_agg = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_away_all'
            target_column_agg_list.append(target_column_agg)
            player_data[target_column_agg] = 0

        # Create new empty player_database with the same columns, the unique DataFrame with aggreage features will be added to this.
        # player_data_aggregate = pd.DataFrame([], columns=player_data.columns)
        player_data_aggregate = []

        # Find the list of unique_ids in the DataFrame
        unique_ids = pd.unique(player_data.sort_values('unique_id')['unique_id'])

        for unique_id in unique_ids:

            if unique_id % 100 == 0:
                print(f"Processing unique_id {unique_id} of {unique_ids[-1]}")

            # Filter the DataFrame to return a DataFrame for every unique player id and then sort on the round.
            player_data_unique_id = player_data_season[player_data_season['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)
            player_data_unique_id_gw = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # Iterate through the sorted dataframe to calulate the aggregate features
            if home is None:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list[k]] = player_data_unique_id[player_data_unique_id[column]>event].shape[0] / \
                                                                                                               player_data_unique_id.shape[0]
            elif home is True:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==True]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list[k]] = 0
                        else:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / \
                                                                                                player_data_unique_id_temp.shape[0]

            elif home is False:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==False]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list[k]] = 0
                        else:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_agg_list] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / \
                                                                                                player_data_unique_id_temp.shape[0]
            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id_gw)

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = pd.concat([player_data_old, player_data_aggregate])
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        # player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data_aggregate


    def calculate_prob_occur_rolling(self, player_data,
                                            path_processed,
                                            filename_player_data,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            season,
                                            target_columns,
                                            gw_curr,
                                            window_size=3,
                                            event=0,
                                            home=None):

        try:
            player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        except:
            print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
        except:
            print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        # try:
        #     player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        # except:
        #     print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data_old = player_data[player_data['season']!=season].copy()
        player_data_old_season = player_data[(player_data['season']==season) & (player_data['round']!=gw_curr)]
        player_data_old = pd.concat([player_data_old, player_data_old_season], axis=0).reset_index(drop=True)

        player_data_season = player_data[player_data['season']==season]
        player_data = player_data[(player_data['season']==season) & (player_data['round']==gw_curr)]

        target_column_list = []

        for target_column in target_columns:
            if home is None:
                target_column = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_any_' + str(window_size)
            elif home is True:
                target_column = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_home_' + str(window_size)
            elif home is False:
                target_column = 'prob_occur_' + target_column + '_greater_than_' + str(event) + '_' + '_away_' + str(window_size)

            # Add placeholder for the stat features
            player_data[target_column] = 0
            target_column_list.append(target_column)


        # Create new empty player_database with the same columns, the unique DataFrame with aggregate features will be added to this.
        player_data_aggregate = []

        # Find the list of unique_ids in the DataFrame
        unique_ids = pd.unique(player_data.sort_values('unique_id')['unique_id'])

        for unique_id in unique_ids:


            if unique_id % 100 == 0:
                print(f"Processing unique_id {unique_id} of {unique_ids[-1]}")

            # Filter the DataFrame to return a DataFrame for every unique player id and then sort on the round.
            player_data_unique_id = player_data_season[player_data_season['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)
            player_data_unique_id_gw = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # if player_data_unique_id.shape[0] > 0:
            I = player_data_unique_id.shape[0]
            offset = window_size - 1

            if home is None:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id.iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)

            if home is True:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id[player_data_unique_id['was_home']==True].iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)

            elif home is False:
                player_data_unique_id_start = []
                player_data_unique_id_start_df = player_data_unique_id[player_data_unique_id['was_home']==False].iloc[:offset, :].copy()

                if player_data_unique_id_start_df.shape[0] < offset:
                    player_data_unique_id_start_df = pd.DataFrame([], columns=player_data_unique_id.columns)
                    for i in range(offset):
                        player_data_unique_id_start_df = pd.concat([player_data_unique_id_start_df, player_data_unique_id.iloc[[0]]], axis=0)
                else:
                    for i in range(offset):
                        player_data_unique_id_start_df.iloc[i, :] = player_data_unique_id_start_df.iloc[0, :]

                player_data_unique_id_start.append(player_data_unique_id_start_df)
                player_data_unique_id = pd.concat([pd.concat(player_data_unique_id_start, axis=0), player_data_unique_id])
                player_data_unique_id = player_data_unique_id.reset_index(level=0, drop=True)


            if home is None:
                # if player_data_unique_id.shape[0] > offset:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_list[k]] = player_data_unique_id[player_data_unique_id[column]>event].iloc[-window_size:].shape[0] / window_size

            elif home is True:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==True].iloc[-window_size:, :]
                    for k, column in enumerate(target_columns):
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_list[k]] = 0
                        else:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_list[k]] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / window_size

            elif home is False:
                for i in range(0, player_data_unique_id_gw.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id[player_data_unique_id['was_home']==False].iloc[-window_size:, :]
                    for k, column in enumerate(target_columns):
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_list[k]] = 0
                        else:
                            player_data_unique_id_gw.loc[player_data_unique_id_gw.index[i], target_column_list[k]] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / window_size


            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id_gw)

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = pd.concat([player_data_old, player_data_aggregate])
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        # player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data_aggregate


    def combine_player_database(self, player_data_gw,
                                path_processed,
                                filename_player_data):

        try:
            player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        except:
            print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        player_data = pd.concat([player_data, player_data_gw], axis=0)
        # player_data.to_csv(path.join(path_processed, filename_player_data), index=False)
        return player_data



    def scrape_league_standings(self, path_league_data_full,
                                path_league_data,
                                league_id,
                                league_type='classic'):

        if league_type =='classic':
            url = 'https://fantasy.premierleague.com/api/leagues-classic/' + str(league_id) + '/standings/'
            r = requests.get(url)
            json = r.json()
            ids = []
            entry_name = []

            for item in json['standings']['results']:
                ids.append(item['entry'])
                entry_name.append(item['entry_name'])

            league_standings = pd.DataFrame(json['standings']['results'])
            league_standings.to_csv(path_league_data, index=False)

            league_data_full = None


            for id in ids:
                url = 'https://fantasy.premierleague.com/api/entry/' + str(id) + '/history/'
                r = requests.get(url)
                json = r.json()
                if league_data_full is None:
                    league_data_full = pd.DataFrame(json['current'])
                    league_data_full['id'] = id
                else:
                    league_data_full_temp = pd.DataFrame(json['current'])
                    league_data_full_temp['id'] = id
                    league_data_full = pd.concat([league_data_full, league_data_full_temp])

            league_data_full['total_event_transfers_cost'] = 0

            unique_ids = league_data_full['id'].unique()
            for unique_id in unique_ids:
                league_data_full_temp = league_data_full[league_data_full['id']==unique_id].copy()
                for i in range(league_data_full_temp.shape[0]):
                    if i ==1:
                        league_data_full_temp['total_event_transfers_cost'].iloc[i] = league_data_full_temp['event_transfers_cost'].iloc[i]
                    else:
                        league_data_full_temp['total_event_transfers_cost'].iloc[i] = league_data_full_temp['event_transfers_cost'].iloc[i] + league_data_full_temp['total_event_transfers_cost'].iloc[i-1]

                    league_data_full[league_data_full['id']==unique_id] = league_data_full_temp

            league_data_full = league_data_full.rename(columns={"event": "round"})
            league_data_full.to_csv(path_league_data_full, index=False)


    def process_database_model(self, path_processed,
                               filename_modelling_db,
                               filename_player_data,
                               team_stats):

        # 1. make sure all rounds go from 1-38 +++++++++++++++
        # 2. make sure all players have rounds 1-38?
        # 3. One-hot encode columns
        # 4. Create feature which is the points obtained in the next gw.

        try:
            player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        except:
            print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        try:
            team_stats = pd.read_csv(path.join(path_processed, team_stats))
        except:
            print('Can\'t find the team_stats.csv file, either the path specified is incorrect or it hasn\'t been created yet')

        model_db = player_data.copy()

        model_db = self.one_hot_encode(model_db, 'was_home', drop=False)
        model_db = self.one_hot_encode(model_db, 'element_type', drop=False)

        model_db['points_next'] = 0
        unique_ids = model_db['unique_id'].unique()

        team_stats = team_stats.drop(columns=['team_name'])
        team_stats = team_stats.drop(columns=['team_unique_id'])
        team_stats = team_stats.drop(columns=['position'])
        team_stats = team_stats.drop(columns=['team_id_against'])
        team_stats = team_stats.drop(columns=['team_unique_id_against'])
        team_stats = team_stats.drop(columns=['against_position'])
        team_stats = team_stats.drop(columns=['win'])
        team_stats = team_stats.drop(columns=['draw'])
        team_stats = team_stats.drop(columns=['loss'])
        team_stats = team_stats.drop(columns=['team_score'])
        team_stats = team_stats.drop(columns=['team_concede'])
        team_stats = team_stats.drop(columns=['total_wins'])
        team_stats = team_stats.drop(columns=['total_draws'])
        team_stats = team_stats.drop(columns=['total_losses'])
        team_stats = team_stats.drop(columns=['was_home'])
        team_stats = team_stats.drop(columns=['against_team_name'])
        team_stats = team_stats.drop(columns=['team_results_all'])
        team_stats = team_stats.drop(columns=['team_results_home'])
        team_stats = team_stats.drop(columns=['team_results_away'])
        team_stats = team_stats.drop(columns=['team_score_all'])
        team_stats = team_stats.drop(columns=['team_score_home'])
        team_stats = team_stats.drop(columns=['team_score_away'])
        team_stats = team_stats.drop(columns=['team_concede_all'])
        team_stats = team_stats.drop(columns=['team_concede_home'])
        team_stats = team_stats.drop(columns=['team_concede_away'])

        # team_stats['round'] = team_stats['round'] - 1
        # team_stats['round'] = team_stats[team_stats['round'] > 0]

        # print(model_db.shape)
        #
        # model_db = model_db.merge(team_stats, on=['season', 'team_id', 'round'], how='inner')
        #
        # print(model_db.shape)

        model_db_list = []

        for unique_id in unique_ids:
            print(f'Processing {unique_id} of {np.max(unique_ids)}')
            player_data_temp = model_db[model_db['unique_id']==unique_id].sort_values('round')
            # player_data_temp = player_data_temp[player_data_temp['round']<player_data_temp['round'].max()].sort_values('round')
            for i in range(player_data_temp.shape[0]-1):
                player_data_temp['points_next'].iloc[i] = player_data_temp['total_points'].iloc[i+1]

            model_db_list.append(player_data_temp)

        model_db = pd.concat(model_db_list, axis=0).reset_index(drop=True)

        model_db_row_list = []
        team_stats_row_list = []

        for i in range(model_db.shape[0]):
            model_db_row = model_db.iloc[i, :]
            row_round = model_db_row['round']+1
            row_season = model_db_row['season']
            row_team = model_db_row['team_id']
            team_stats_row = team_stats[(team_stats['round']==row_round) & (team_stats['season']==row_season) & (team_stats['team_id']==row_team)]

            # model_db_row_list.append(model_db_row)
            team_stats_row_list.append(team_stats_row)


        team_stats_df = pd.concat(team_stats_row_list, axis=0).reset_index(drop=True)
        model_db = pd.concat([model_db.reset_index(drop=True), team_stats_df], axis=1).reset_index(drop=True)
        # model_db_row = pd.concat([model_db_row.to_frame().T.reset_index(drop=True), row_team_stats.reset_index(drop=True)], axis=1)

        # model_db = pd.concat(model_db_row_list, axis=0).reset_index(drop=True)

        columns = list(model_db.columns)
        columns_final = columns.copy()

        columns_final.remove('kickoff_time')
        columns_final.remove('team_name')
        columns_final.remove('team_played')
        columns_final.remove('next_fixture_team')
        columns_final.remove('next_fixture_played')
        columns_final.remove('team_unique_id')
        columns_final.remove('team_id')

        for column in columns:
            if column.split('_')[0] == 'range' or column.split('_')[0] == 'std' or column.split('_')[0] == 'se':
                columns_final.remove(column)

        model_db = model_db[columns_final]

        model_db.to_csv(path.join(path_processed, filename_modelling_db), index=False)

    def one_hot_encode(self, data,
                       column_name,
                       drop=True):

        data_onehot = pd.get_dummies(data[column_name],prefix=column_name)
        if drop is True:
            data = data.drop(columns=[column_name])
        data = pd.concat([data, data_onehot], axis=1)

        return data

    def scrape_team_information(self, email, password, team_id):

        session = requests.session()
        url = 'https://users.premierleague.com/accounts/login/'

        payload = {
            'password': password,
            'login': email,
            'redirect_uri': 'https://fantasy.premierleague.com/a/login',
            'app': 'plfpl-web'
        }

        session.post(url, data=payload)

        response = session.get('https://fantasy.premierleague.com/api/my-team/' + str(team_id)).json()

        team_picks = pd.DataFrame(response['picks'])

        return team_picks


    def scrape_transfer_information(self, email, password, team_id):

        session = requests.session()
        url = 'https://users.premierleague.com/accounts/login/'

        payload = {
            'password': password,
            'login': email,
            'redirect_uri': 'https://fantasy.premierleague.com/a/login',
            'app': 'plfpl-web'
        }

        session.post(url, data=payload)

        response = session.get('https://fantasy.premierleague.com/api/my-team/' + str(team_id)).json()

        transfers = pd.Series(response['transfers'])

        return transfers


    def determine_current_gw(self):

        events = self.scrape_bootstrap_static(keys=['events'])['events']

        curr_gw_flag = False
        gw_curr = 0
        i = 0

        while curr_gw_flag is False:
            # print(events['finished'].values[i])
            # print(events['finished'].values[i] == True)
            # print(events['finished'].iloc[i])
            if events['finished'].values[i] == True:
                i += 1
            else:
                curr_gw_flag = True
                gw_curr = events['id'].iloc[i-1]

        return gw_curr






