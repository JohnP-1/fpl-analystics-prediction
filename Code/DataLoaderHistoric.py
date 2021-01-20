import numpy as np
import pandas as pd
from os import path
import os
import scipy.stats as stats
import collections
import json

#Need to convert the opponent team to the unique team id!!! for both he current fixture as well as all future fixtures.


class DataLoaderHistoric():

    def __init__(self):
        pass


    def check_file_exists(self, file_path):
        """
        Checks if a file exists.

        :param file_path: Str --> Path to file
        :return: Bool
        """

        return path.exists(file_path)


    def create_player_database(self, file_path,
                               columns):
        """
        Function used to create the player database .csv file.

        :param file_path: Str --> path to save file including filename
        :param columns: List --> List of column names to use in DataFrame
        :return: None
        """

        data = pd.DataFrame([], columns=columns)
        data.to_csv(file_path, index=False)


    def load_player_database(self, file_path,
                             encoding='UTF-8'):
        """
        Load the player database .csv file into a pandas DataFrame.

        :param file_path: Str --> path to load file including filename
        :param encoding: Str --> File encoding
        :return: DataFrame object
        """

        return pd.read_csv(file_path, encoding=encoding)


    def load_gw(self, file_path,
                encoding='UTF-8'):
        """
        Load a gw .csv file into a pandas DataFrame.

        :param file_path: Str --> path to load file including filename
        :param encoding: Str --> File encoding
        :return: DataFrame object
        """

        return pd.read_csv(file_path, encoding=encoding)


    def save_gw(self, data,
                file_path,
                encoding='UTF-8'):
        """
        Save a gw .csv file from a DataFrame.

        :param data:
        :param file_path:
        :param encoding:
        :return:
        """

        return data.to_csv(file_path, encoding=encoding, index=False)


    def load_raw_player_data(self, file_path,
                             encoding='UTF-8'):
        """
        Load a gw .csv file into a pandas DataFrame.

        :param file_path: Str --> path to load file including filename
        :param encoding: Str --> File encoding
        :return: DataFrame object
        """

        return pd.read_csv(file_path, encoding=encoding)


    def path_data_season(self, year):
        """
        Function used to determine the file path to the folder containing all the data for a specified season. The season is specified by the first year in the season. For example the year passed to the function for the 2019/20 season would be 2019.

        :param year: Int --> Year of season to be selected
        :return: Str --> Path to the selected season
        """

        path_data = path.join(path.dirname(path.dirname(__file__)), 'Data')
        if year == 2016:
            path_season = path.join(path_data, '2016-17')
        elif year == 2017:
            path_season = path.join(path_data, '2017-18')
        elif year == 2018:
            path_season = path.join(path_data, '2018-19')
        elif year == 2019:
            path_season = path.join(path_data, '2019-20')
        elif year == 2020:
            path_season = path.join(path_data, '2020-21')

        return path_season


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
        file_GW_raw = 'players_raw.csv'
        data_player_raw = self.load_raw_player_data(path.join(self.path_data_season(year), file_GW_raw))

        data_gw['team'] = np.zeros(data_gw.shape[0])

        for i in range(data_gw.shape[0]):
            player_id = data_gw['element'].iloc[i]
            player_team = data_player_raw[data_player_raw['id']==player_id]['team']
            data_gw['team'].iloc[i] = int(player_team.values)

        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', file_GW), encoding='UTF-8', index=False)


    def add_position(self, gw, year):

        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
        file_GW_raw = 'players_raw.csv'
        data_player_raw = self.load_raw_player_data(path.join(self.path_data_season(year), file_GW_raw))


        data_player_raw = data_player_raw[['id', 'element_type']]
        data_player_raw = data_player_raw.rename(columns={"id": "element"})

        data_gw = data_gw.merge(data_player_raw, on='element')
        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', file_GW), encoding='UTF-8', index=False)



    def process_league_standings(self, year,
                                 gw):
        """
        Function used to process the league standings
        :param year:
        :param gw:
        :return:
        """

        teams = pd.read_csv(path.join(self.path_data_season(year), 'teams.csv'))
        table = teams.copy()
        table['points'] = 0
        table['wins'] = 0
        table['draws'] = 0
        table['losses'] = 0
        table['goals_for'] = 0
        table['goals_against'] = 0
        table['goals_diff'] = 0
        table['played'] = 0
        table['yc'] = 0
        table['rc'] = 0
        table['position'] = 0

        for gw_curr in range(1, gw+1):
            # print(gw_curr)
            fixtures = [-1]

            file_GW = 'gw' + str(gw_curr) + '.csv'
            data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
            data_gw = data_gw.dropna()

            for i in range(data_gw.shape[0]):
                player_team = data_gw['team'].iloc[i]
                table['yc'][table['id']==player_team] += data_gw['yellow_cards'].iloc[i]
                table['rc'][table['id']==player_team] += data_gw['red_cards'].iloc[i]
                if data_gw['was_home'].iloc[i] == True:
                    home = int(data_gw['team'].iloc[i])
                    away = int(data_gw['opponent_team'].iloc[i])
                else:
                    home = int(data_gw['opponent_team'].iloc[i])
                    away = int(data_gw['team'].iloc[i])

                fixture = stats.mode(data_gw[data_gw['fixture'] == data_gw['fixture'].iloc[i]]['fixture'])
                team_fixture = stats.mode(data_gw[data_gw['fixture'] == data_gw['fixture'].iloc[i]]['team'])[0][0]

                if player_team != team_fixture:
                    fixture = -1

                if fixture not in fixtures:
                    # print(fixture)
                    fixtures.append(fixture)
                    table['played'][table['id'] == home] += 1
                    table['played'][table['id'] == away] += 1
                    home_score = int(data_gw['team_h_score'].iloc[i])
                    away_score = int(data_gw['team_a_score'].iloc[i])
                    table['goals_for'][table['id'] == home] += home_score
                    table['goals_against'][table['id'] == home] += away_score
                    table['goals_for'][table['id'] == away] += away_score
                    table['goals_against'][table['id'] == away] += home_score
                    table['goals_diff'][table['id'] == home] = table['goals_for'][table['id'] == home] - table['goals_against'][table['id'] == home]
                    table['goals_diff'][table['id'] == away] = table['goals_for'][table['id'] == away] - table['goals_against'][table['id'] == away]

                    if home_score > away_score:
                        home_win = True
                        away_win = False
                        draw = False
                    elif home_score == away_score:
                        home_win = False
                        away_win = False
                        draw = True
                    else:
                        home_win = False
                        away_win = True
                        draw = False

                    if home_win is True:
                        table['points'][table['id'] == home] += 3
                        table['wins'][table['id'] == home] += 1
                        table['losses'][table['id'] == away] += 1
                    elif away_win is True:
                        table['points'][table['id'] == away] += 3
                        table['wins'][table['id'] == away] += 1
                        table['losses'][table['id'] == home] += 1
                    elif draw is True:
                        table['points'][table['id'] == home] += 1
                        table['points'][table['id'] == away] += 1
                        table['draws'][table['id'] == home] += 1
                        table['draws'][table['id'] == away] += 1

        table = table.sort_values(by=['points', 'goals_diff', 'goals_for'], ascending=False)
        table['position'] = np.arange(1, table.shape[0]+1)
        table = table.sort_values(by='id', ascending=True)

        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
        data_gw = data_gw.dropna()

        data_gw['points'] = 0
        data_gw['wins'] = 0
        data_gw['draws'] = 0
        data_gw['losses'] = 0
        data_gw['goals_for'] = 0
        data_gw['goals_against'] = 0
        data_gw['goals_diff'] = 0
        data_gw['played'] = 0
        data_gw['yc'] = 0
        data_gw['rc'] = 0
        data_gw['position'] = 0
        data_gw['season'] = year

        for i in range(data_gw.shape[0]):
            player_team = data_gw['team'].iloc[i]
            data_gw['points'][i] = table[table['id'] == player_team]['points']
            data_gw['wins'][i] = table[table['id'] == player_team]['wins']
            data_gw['draws'][i] = table[table['id'] == player_team]['draws']
            data_gw['losses'][i] = table[table['id'] == player_team]['losses']
            data_gw['goals_for'][i] = table[table['id'] == player_team]['goals_for']
            data_gw['goals_against'][i] = table[table['id'] == player_team]['goals_against']
            data_gw['goals_diff'][i] = table[table['id'] == player_team]['goals_diff']
            data_gw['played'][i] = table[table['id'] == player_team]['played']
            data_gw['yc'][i] = table[table['id'] == player_team]['yc']
            data_gw['rc'][i] = table[table['id'] == player_team]['rc']
            data_gw['position'][i] = table[table['id'] == player_team]['position']

        table_GW = 'league_table_gw' + str(gw) + '.csv'
        table.to_csv(path.join(self.path_data_season(year), 'gws', table_GW), encoding='UTF-8', index=False)

        data_GW = 'gw' + str(gw) + '.csv'
        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', data_GW), encoding='UTF-8', index=False)


    def process_fixtures(self, year,
                         gw):
        """

        :param year:
        :param gw:
        :return:
        """

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

        gw_next = gw + 1
        if gw_next < 38:
            file_GW_next = 'gw' + str(gw_next) + '.csv'
            data_gw_next = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW_next))

            file_league_table_curr = 'league_table_gw' + str(gw_next) + '.csv'
            teams_next = self.load_gw(path.join(self.path_data_season(year), 'gws', file_league_table_curr))

            for i in range(data_gw.shape[0]):
                player = data_gw['element'].iloc[i]
                try:
                    team = data_gw_next[data_gw_next['element']==player]['opponent_team'].values[0]
                    data_gw['next_fixture_team'][data_gw['element']==player] = data_gw_next[data_gw_next['element']==player]['opponent_team'].values[0]
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
                except:
                    pass

        data_GW = 'gw' + str(gw) + '.csv'
        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', data_GW), encoding='UTF-8', index=False)



    def process_playernames(self, year,
                            gw):
        """

        :param year:
        :param gw:
        :return:
        """

        file_GW = 'gw' + str(gw) + '.csv'
        data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
        data_gw['name_first'] = ''
        data_gw['name_last'] = ''

        for i in range(data_gw.shape[0]):
            names = data_gw['name'].iloc[i].split('_')
            data_gw['name_first'].iloc[i] = names[0]
            data_gw['name_last'].iloc[i] = names[1]

        data_gw.to_csv(path.join(self.path_data_season(year), 'gws', file_GW), encoding='UTF-8', index=False)



    def create_player_data(self, path_processed,
                               filename):
        """

        :param path_processed:
        :param filename:
        :return:
        """

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

        # Check player database exists
        if self.check_file_exists(path.join(path_processed, filename)) is False:
            self.create_player_database(path.join(path_processed, filename), columns=columns)


    def create_team_metadata(self, path_processed,
                             filename):
        """

        :param path_processed:
        :param filename:
        :return:
        """

        columns = ['team_name',
                    'team_id',
                    'season',
                   'team_unique_id']

        # Check player metadata exists
        if self.check_file_exists(path.join(path_processed, filename)) is False:
            self.create_player_database(path.join(path_processed, filename), columns=columns)



    def create_player_metadata(self, path_processed,
                               filename):

        columns = ['name',
                   'name_first',
                   'name_last',
                   'element_type',
                    'season',
                    'unique_id',
                    'team_id',
                   'team_unique_id']

        if self.check_file_exists(path.join(path_processed, filename)) is False:
            self.create_player_database(path.join(path_processed, filename), columns=columns)


    def process_team_metadata(self, path_processed,
                              filename_team_metadata,
                              seasons):
        """

        :param path_processed:
        :param filename_team_metadata:
        :param seasons:
        :return:
        """

        self.create_team_metadata(path_processed, filename_team_metadata)

        team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))

        for year in seasons:
            #Only need to look at one gw per season as the teams won't change over a season
            file_GW = 'gw' + str(1) + '.csv'
            # data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
            team_data = self.load_gw(path.join(self.path_data_season(year), 'teams.csv'))

            for i in range(team_data.shape[0]):

                team = [team_data['name'].iloc[i], year]
                team_id = team_data['id'].iloc[i]
                team_name = team_data['name'].iloc[i]
                team_exists = False

                team_names = team_metadata[['team_name']].values
                if team_metadata.shape[0] > 0:
                    teams_processed = team_metadata[['team_name', 'season']].values

                    # Using Counter
                    for elem in teams_processed:
                        if collections.Counter(elem) == collections.Counter(team):
                            team_exists = True

                if team_exists is False:
                    if team_name not in team_names:
                        # team_metadata
                        if team_metadata.shape[0] > 0:
                            unique_id = team_metadata['team_unique_id'].max() + 1
                        else:
                            unique_id = 1
                        team_metadata_temp = pd.DataFrame([[team[0], team_id, year, unique_id]],
                                                          columns=team_metadata.columns)
                    else:
                        unique_id = team_metadata[team_metadata['team_name'] == team_name]['team_unique_id'].values[0]
                        team_metadata_temp = pd.DataFrame([[team[0], team_id, year, unique_id]],
                                                          columns=team_metadata.columns)

                    team_metadata = pd.concat([team_metadata, team_metadata_temp])


        team_metadata.to_csv(path.join(path_processed, filename_team_metadata), index=False)


    def process_player_metadata(self, path_processed,
                                filename_player_metadata,
                                filename_team_metadata,
                                seasons,
                                gws):
        """

        :param path_processed:
        :param filename_player_metadata:
        :param filename_team_metadata:
        :param seasons:
        :param gws:
        :return:
        """

        self.create_player_metadata(path_processed, filename_player_metadata)

        player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
        team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))


        for year in seasons:
            for gw in gws:
                print(f'Processing GW {gw} of season {year}')
                file_GW = 'gw' + str(gw) + '.csv'
                data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
                data_gw_player = data_gw[['name_first', 'name_last', 'season']]


                for i in range(data_gw_player.shape[0]):
                    player = data_gw_player.iloc[i, :]

                    player_exists = False

                    if player_metadata.shape[0] > 0:
                        players_processed = player_metadata[['name_first', 'name_last', 'season']].values

                        # Using Counter
                        for elem in players_processed:
                            if collections.Counter(elem) == collections.Counter(player):
                                player_exists = True

                    if player_exists is False:
                        team = data_gw['team'].iloc[i]
                        for j in range(team_metadata.shape[0]):
                            if (team_metadata['team_id'].iloc[j]==team) and (team_metadata['season'].iloc[j]==year):
                                team_unique_id = team_metadata['team_unique_id'].iloc[j]


                        for j in range(team_metadata.shape[0]):
                            if (team_metadata['team_id'].iloc[j] == team) and (team_metadata['season'].iloc[j] == year):
                                unique_id = player_metadata.shape[0]+1

                        player_temp = [data_gw['name_first'].iloc[i]+'_'+data_gw['name_last'].iloc[i],
                                       data_gw['name_first'].iloc[i],
                                       data_gw['name_last'].iloc[i],
                                       data_gw['element_type'].iloc[i],
                                       data_gw['season'].iloc[i],
                                       unique_id,
                                       team,
                                       team_unique_id]

                        player_temp = pd.DataFrame([player_temp], columns=player_metadata.columns)
                        player_metadata = pd.concat([player_metadata, player_temp])

        player_metadata.to_csv(path.join(path_processed, filename_player_metadata), index=False)



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

        self.create_player_data(path_processed, filename_player_data)
        player_data = pd.read_csv(path.join(path_processed, filename_player_data))

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

                gw_next = gw + 1
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
        player_data.to_csv(path.join(path_processed, filename_player_data), index=False)


    def calculate_aggregate_features(self, path_processed,
                                            filename_player_data,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            target_columns,
                                            home=None):


            try:
                player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
            except:
                print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

            try:
                team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
            except:
                print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

            try:
                player_data = pd.read_csv(path.join(path_processed, filename_player_data))
            except:
                print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

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
                player_data_unique_id = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

                # Iterate through the sorted dataframe to calulate the aggregate features
                if home is None:
                    for i in range(0, player_data_unique_id.shape[0]):
                        player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = np.sum(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)
                elif home is True:
                    for i in range(0, player_data_unique_id.shape[0]):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==True]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = np.sum(player_data_unique_id_temp[target_columns].values, axis=0)

                elif home is False:
                    for i in range(0, player_data_unique_id.shape[0]):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==False]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = np.sum(player_data_unique_id_temp[target_columns].values, axis=0)
                # Concatonate the DataFrames
                player_data_aggregate.append(player_data_unique_id)

            player_data_aggregate = pd.concat(player_data_aggregate)
            player_data_aggregate = player_data_aggregate.drop_duplicates()
            player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)


    def calculate_stat_features(self, path_processed,
                                        filename_player_data,
                                        filename_player_metadata,
                                        filename_team_metadata,
                                        target_columns,
                                        home=None):


                try:
                    player_metadata = pd.read_csv(path.join(path_processed, filename_player_metadata))
                except:
                    print('Can\'t find the player_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

                try:
                    team_metadata = pd.read_csv(path.join(path_processed, filename_team_metadata))
                except:
                    print('Can\'t find the team_metadata.csv file, either the path specified is incorrect or it hasn\'t been created yet')

                try:
                    player_data = pd.read_csv(path.join(path_processed, filename_player_data))
                except:
                    print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

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
                    player_data_unique_id = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

                    # Iterate through the sorted dataframe to calulate the aggregate features
                    if home is None:
                        for i in range(0, player_data_unique_id.shape[0]):
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = np.mean(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = np.median(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = np.std(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = np.std(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)/np.sqrt(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].shape[0])
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = np.max(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0) - np.min(player_data_unique_id.loc[player_data_unique_id.index[:i+1], target_columns].values, axis=0)
                    elif home is True:
                        for i in range(0, player_data_unique_id.shape[0]):
                            player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==True]
                            if player_data_unique_id_temp.shape[0] == 0:
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = 0
                            else:
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = np.std(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = np.std(player_data_unique_id_temp[target_columns].values, axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

                    elif home is False:
                        for i in range(0, player_data_unique_id.shape[0]):
                            player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==False]
                            if player_data_unique_id_temp.shape[0] == 0:
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = 0
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = 0
                            else:
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = np.std(player_data_unique_id_temp[target_columns].values, axis=0)
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = np.std(player_data_unique_id_temp[target_columns].values, axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                                player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)


                    player_data_aggregate.append(player_data_unique_id)
                    # Concatonate the DataFrames
                player_data_aggregate = pd.concat(player_data_aggregate)
                player_data_aggregate = player_data_aggregate.drop_duplicates()

                player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)


    def calculate_statrolling_features(self, path_processed,
                                            filename_player_data,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            target_columns,
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

            try:
                player_data = pd.read_csv(path.join(path_processed, filename_player_data))
            except:
                print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

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
                player_data_unique_id = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

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
                    if player_data_unique_id.shape[0] > offset:
                        # print(player_data_unique_id)
                        for i in range(0, player_data_unique_id.shape[0]-offset):
                            # print(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values)
                            player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_mean_list] = np.mean(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_median_list] = np.median(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_std_list] = np.std(np.array(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, dtype=np.float64), axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_se_list] = np.std(np.array(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, dtype=np.float64), axis=0)/np.sqrt(window_size)
                            player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_range_list] = np.max(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, axis=0) - np.min(player_data_unique_id.loc[player_data_unique_id.index[i:i+window_size], target_columns].values, axis=0)
                elif home is True:
                    for i in range(offset, player_data_unique_id.shape[0]):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==True].iloc[-window_size:, :]

                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

                elif home is False:
                    for i in range(offset, player_data_unique_id.shape[0]):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==False].iloc[-window_size:, :]

                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = 0
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_mean_list] = np.mean(player_data_unique_id_temp[target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_median_list] = np.median(player_data_unique_id_temp[target_columns].values, axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_std_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_se_list] = np.std(np.array(player_data_unique_id_temp[target_columns].values, dtype=np.float64), axis=0)/np.sqrt(player_data_unique_id_temp[target_columns].shape[0])
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_range_list] = np.max(player_data_unique_id_temp[target_columns].values, axis=0) - np.min(player_data_unique_id_temp[target_columns].values, axis=0)

                # Concatonate the DataFrames
                player_data_aggregate.append(player_data_unique_id.iloc[offset:, :])

            player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
            player_data_aggregate = player_data_aggregate.drop_duplicates()
            player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)


    def calculate_prob_occur(self, path_processed,
                                    filename_player_data,
                                    filename_player_metadata,
                                    filename_team_metadata,
                                    target_columns,
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

        try:
            player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        except:
            print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

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
            player_data_unique_id = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

            # Iterate through the sorted dataframe to calulate the aggregate features
            if home is None:
                for i in range(0, player_data_unique_id.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list[k]] = player_data_unique_id[player_data_unique_id[column]>event].iloc[:i+1, :].shape[0] / \
                                                                                                               player_data_unique_id.iloc[:i+1, :].shape[0]
            elif home is True:
                for i in range(0, player_data_unique_id.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==True]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list[k]] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].iloc[:i+1, :].shape[0] / \
                                                                                                player_data_unique_id_temp.iloc[:i+1, :].shape[0]

            elif home is False:
                for i in range(0, player_data_unique_id.shape[0]):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==False]
                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg_list[k]] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_agg] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].iloc[:i+1, :].shape[0] / \
                                                                                                player_data_unique_id_temp.iloc[:i+1, :].shape[0]
            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id)

        player_data_aggregate = pd.concat(player_data_aggregate)
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)


    def calculate_prob_occur_rolling(self, path_processed,
                                            filename_player_data,
                                            filename_player_metadata,
                                            filename_team_metadata,
                                            target_columns,
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

        try:
            player_data = pd.read_csv(path.join(path_processed, filename_player_data))
        except:
            print('Can\'t find the player_data.csv file, either the path specified is incorrect or it hasn\'t been created yet')

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
            player_data_unique_id = player_data[player_data['unique_id']==unique_id].sort_values('round', ascending=True).reset_index(level=0, drop=True)

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
                for i in range(0, player_data_unique_id.shape[0]-offset):
                    for k, column in enumerate(target_columns):
                        player_data_unique_id.loc[player_data_unique_id.index[i+offset], target_column_list[k]] = player_data_unique_id[player_data_unique_id[column]>event].iloc[i:i+window_size].shape[0] / window_size

            elif home is True:
                for i in range(offset, player_data_unique_id.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==True].iloc[-window_size:, :]
                    for k, column in enumerate(target_columns):

                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_list[k]] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_list[k]] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / window_size

            elif home is False:
                for i in range(offset, player_data_unique_id.shape[0]):
                    player_data_unique_id_temp = player_data_unique_id.iloc[:i+1, :][player_data_unique_id.iloc[:i+1, :]['was_home']==False].iloc[-window_size:, :]
                    for k, column in enumerate(target_columns):

                        if player_data_unique_id_temp.shape[0] == 0:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_list[k]] = 0
                        else:
                            player_data_unique_id.loc[player_data_unique_id.index[i], target_column_list[k]] = player_data_unique_id_temp[player_data_unique_id_temp[column]>event].shape[0] / window_size


            # Concatonate the DataFrames
            player_data_aggregate.append(player_data_unique_id.iloc[offset:, :])

        player_data_aggregate = pd.concat(player_data_aggregate, axis=0)
        player_data_aggregate = player_data_aggregate.drop_duplicates()
        player_data_aggregate.to_csv(path.join(path_processed, filename_player_data), index=False)



    def process_fixtures_season(self, year,
                         path_processed):
        """
        Function used to process the league standings
        :param year:
        :param gw:
        :return:
        """

        teams = pd.read_csv(path.join(path_processed, 'team_metadata.csv'))
        # table = teams.copy()

        fixtures = pd.DataFrame([])

        fixtures['fixture'] = 0
        fixtures['round'] = 0
        fixtures['team_home'] = 0
        fixtures['uniqueid_home'] = 0
        fixtures['team_away'] = 0
        fixtures['uniqueid_away'] = 0
        fixtures['team_home_gs'] = 0
        fixtures['team_home_gc'] = 0
        fixtures['team_away_gs'] = 0
        fixtures['team_away_gc'] = 0
        fixtures['team_home_win'] = 0
        fixtures['team_home_draw'] = 0
        fixtures['team_home_loss'] = 0
        fixtures['team_away_win'] = 0
        fixtures['team_away_draw'] = 0
        fixtures['team_away_loss'] = 0

        files = os.listdir(path.join(self.path_data_season(year), 'gws'))

        gw_list = []
        for file in files:
            if file[0] == 'l':
                file = file.split('_')[-1]
                file = file.split('.')[-0]
                gw_list.append(int(file[2:]))

        gw = max(gw_list)

        fixture_data = []
        for gw_curr in range(1, gw+1):
            file_GW = 'gw' + str(gw_curr) + '.csv'
            data_gw = self.load_gw(path.join(self.path_data_season(year), 'gws', file_GW))
            data_gw = data_gw.dropna()

            fixtures_processed = []

            # data_gw_curr = data_gw[data_gw['round']==gw]
            for i in range(data_gw.shape[0]):
                # print('player', i)
                player_team = data_gw['team'].iloc[i]
                fixture = data_gw['fixture'].iloc[i]

                if data_gw[(data_gw['team']==player_team) & (data_gw['fixture']==fixture)].shape[0] >= 11:
                    if fixture not in fixtures_processed:
                        fixtures_processed.append(fixture)

                        data_gw_curr = data_gw[(data_gw['team']==player_team) & (data_gw['fixture']==fixture)]
                        if data_gw['was_home'].iloc[i] == True:
                            home_team = int(stats.mode(data_gw_curr['team'])[0][0])
                            uniqueid_home = teams[(teams['team_id']==home_team) & (teams['season']==year)]['team_unique_id'].values[0]
                            away_team = int(stats.mode(data_gw_curr['opponent_team'])[0][0])
                            uniqueid_away = teams[(teams['team_id']==away_team) & (teams['season']==year)]['team_unique_id'].values[0]

                        else:
                            home_team = int(stats.mode(data_gw_curr['opponent_team'])[0][0])
                            uniqueid_home = teams[(teams['team_id']==home_team) & (teams['season']==year)]['team_unique_id'].values[0]
                            away_team = int(stats.mode(data_gw_curr['team'])[0][0])
                            uniqueid_away = teams[(teams['team_id']==away_team) & (teams['season']==year)]['team_unique_id'].values[0]


                        team_home_gs = int(stats.mode(data_gw_curr['team_h_score'])[0][0])
                        team_away_gs = int(stats.mode(data_gw_curr['team_a_score'])[0][0])
                        team_home_gc = int(stats.mode(data_gw_curr['team_a_score'])[0][0])
                        team_away_gc = int(stats.mode(data_gw_curr['team_h_score'])[0][0])

                        if team_home_gs > team_away_gs:
                            team_home_win = 1
                            team_home_draw = 0
                            team_home_loss = 0
                            team_away_win = 0
                            team_away_draw = 0
                            team_away_loss = 1
                        elif team_home_gs < team_away_gs:
                            team_home_win = 0
                            team_home_draw = 0
                            team_home_loss = 1
                            team_away_win = 1
                            team_away_draw = 0
                            team_away_loss = 0
                        elif team_home_gs == team_away_gs:
                            team_home_win = 0
                            team_home_draw = 1
                            team_home_loss = 0
                            team_away_win = 0
                            team_away_draw = 1
                            team_away_loss = 0

                        fixture_data_dp = pd.DataFrame([[fixture,
                                                         gw_curr,
                                                         home_team,
                                                         uniqueid_home,
                                                         away_team,
                                                         uniqueid_away,
                                                         team_home_gs,
                                                         team_home_gc,
                                                         team_away_gs,
                                                         team_away_gc,
                                                         team_home_win,
                                                         team_home_draw,
                                                         team_home_loss,
                                                         team_away_win,
                                                         team_away_draw,
                                                         team_away_loss]], columns=fixtures.columns)
                        fixture_data.append(fixture_data_dp)

        fixtures = pd.concat(fixture_data)
        # print(fixtures.reset_index(drop='index'))
        fixtures.to_csv(path.join(self.path_data_season(year), 'fixture_results.csv'), index=False)


    def process_team_stats_init(self, seasons,
                            path_processed):
        """
        Function used to process the league standings
        :param year:
        :param gw:
        :return:
        """

        columns = ['team_name',
                   'team_id',
                   'season',
                   'team_unique_id',
                   'round',
                   'position',
                   'team_id_against',
                   'team_unique_id_against',
                   'against_position',
                   'win',
                   'draw',
                   'loss',
                   'team_score',
                   'team_concede',
                   'total_wins',
                   'total_draws',
                   'total_losses',
                   'was_home']

        teams = pd.read_csv(path.join(path_processed, 'team_metadata.csv'))
        data_all = []

        for season in seasons:
            fixtures = pd.read_csv(path.join(self.path_data_season(season), 'fixture_results.csv'))
            fixtures = fixtures.sort_values(by='fixture', ascending=True)

            team_data = teams[teams['season']==season].copy().reset_index(drop='index')
            # team_ids = team_data['team_id'].unique()

            files = os.listdir(path.join(self.path_data_season(season), 'gws'))

            gw_list = []
            for file in files:
                if file[0] == 'l':
                    file = file.split('_')[-1]
                    file = file.split('.')[-0]
                    gw_list.append(int(file[2:]))

            gw_max = max(gw_list)

            for gw in range(1, gw_max+1):
                data_list = []
                print('gameweek ', gw)
                file_GW = 'league_table_gw' + str(gw) + '.csv'
                league_data = pd.read_csv(path.join(self.path_data_season(season), 'gws', file_GW))
                fixtures_gw = fixtures[fixtures['round']==gw]

                for fixture in fixtures_gw['fixture'].unique():
                    data = pd.DataFrame([], columns=columns)

                    # Collect data for the home team
                    data['team_id'] = fixtures_gw[fixtures_gw['fixture']==fixture]['team_home']
                    data['season'] = season
                    data['team_unique_id'] = fixtures_gw[fixtures_gw['fixture']==fixture]['uniqueid_home']
                    data['team_name'] = league_data[league_data['id']==data['team_id'].values[0]]['name'].values
                    data['round'] = gw
                    data['position'] = league_data[league_data['id']==data['team_id'].values[0]]['position'].values

                    fixture_curr = fixtures_gw[fixtures_gw['fixture']==fixture]
                    data['team_id_against'] = fixture_curr['team_away'].values[0]
                    data['team_unique_id_against'] = fixture_curr['uniqueid_away'].values[0]
                    data['against_team_name'] = league_data[league_data['id']==data['team_id_against'].values[0]]['name'].values
                    data['against_position'] = league_data[league_data['id']==data['team_id_against'].values[0]]['position'].values
                    data['was_home'] = True
                    data['team_score'] = fixture_curr['team_home_gs'].values[0]
                    data['team_concede'] = fixture_curr['team_home_gc'].values[0]
                    data['win'] = fixture_curr['team_home_win'].values[0]
                    data['draw'] = fixture_curr['team_home_draw'].values[0]
                    data['loss'] = fixture_curr['team_home_loss'].values[0]

                    data['total_wins'] = league_data[league_data['id']==data['team_id'].values[0]]['wins'].values
                    data['total_draws'] = league_data[league_data['id']==data['team_id'].values[0]]['draws'].values
                    data['total_losses'] = league_data[league_data['id']==data['team_id'].values[0]]['losses'].values

                    data_list.append(data)

                    data = pd.DataFrame([], columns=columns)
                    # Collect data for the away team
                    data['team_id'] = fixtures_gw[fixtures_gw['fixture']==fixture]['team_away']
                    data['season'] = season
                    data['team_unique_id'] = fixtures_gw[fixtures_gw['fixture']==fixture]['uniqueid_away']
                    data['team_name'] = league_data[league_data['id']==data['team_id'].values[0]]['name'].values
                    data['round'] = gw
                    data['position'] = league_data[league_data['id']==data['team_id'].values[0]]['position'].values

                    fixture_curr = fixtures_gw[fixtures_gw['fixture']==fixture]
                    data['team_id_against'] = fixture_curr['team_home'].values[0]
                    data['team_unique_id_against'] = fixture_curr['uniqueid_home'].values[0]
                    data['against_team_name'] = league_data[league_data['id']==data['team_id_against'].values[0]]['name'].values
                    data['against_position'] = league_data[league_data['id']==data['team_id_against'].values[0]]['position'].values
                    data['was_home'] = False
                    data['team_score'] = fixture_curr['team_home_gc'].values[0]
                    data['team_concede'] = fixture_curr['team_home_gs'].values[0]
                    data['win'] = fixture_curr['team_away_win'].values[0]
                    data['draw'] = fixture_curr['team_away_draw'].values[0]
                    data['loss'] = fixture_curr['team_away_loss'].values[0]

                    data['total_wins'] = league_data[league_data['id']==data['team_id'].values[0]]['wins'].values
                    data['total_draws'] = league_data[league_data['id']==data['team_id'].values[0]]['draws'].values
                    data['total_losses'] = league_data[league_data['id']==data['team_id'].values[0]]['losses'].values

                    data_list.append(data)

                data_gw = pd.concat(data_list, axis=0)

                file_name = 'team_stats_gw' + str(gw) + '.csv'
                data_gw.to_csv(path.join(self.path_data_season(season), 'gws', file_name), index=False)
                data_all.append(data_gw)

        data_all = pd.concat(data_all, axis=0)
        data_all.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)




    def process_team_stats(self, seasons,
                            path_processed):

        data = pd.read_csv(path.join(path_processed, 'team_stats.csv'))

        team_unique_ids = data['team_unique_id'].unique()

        # Process the team results

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_results_list(data_curr))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_results(data_curr, results_window=3))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_results(data_curr, results_window=4))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_results(data_curr, results_window=5))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_results(data_curr, results_window=10))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)


        # Process the data relating to teams scoring and concedeing
        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_score(data_curr, results_window=3))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_score(data_curr, results_window=4))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_score(data_curr, results_window=5))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            for unique_id in team_unique_ids:
                data_curr = data[(data['team_unique_id']==unique_id) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_team_score(data_curr, results_window=10))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        # Calculate odds
        team_results_list = []

        for season in seasons:
            max_round = data[data['season']==season]['round'].max()
            for round in range(1, max_round+1):
                data_curr = data[(data['round']==round) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_current_game_odds(data_curr, results_window=3))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            max_round = data[data['season']==season]['round'].max()
            for round in range(1, max_round+1):
                data_curr = data[(data['round']==round) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_current_game_odds(data_curr, results_window=4))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            max_round = data[data['season']==season]['round'].max()
            for round in range(1, max_round+1):
                data_curr = data[(data['round']==round) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_current_game_odds(data_curr, results_window=5))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)

        team_results_list = []

        for season in seasons:
            max_round = data[data['season']==season]['round'].max()
            for round in range(1, max_round+1):
                data_curr = data[(data['round']==round) & (data['season']==season)]
                if data_curr.shape[0] > 0:
                    team_results_list.append(self.process_current_game_odds(data_curr, results_window=10))

        data = pd.concat(team_results_list, axis=0)
        data.to_csv(path.join(path_processed, 'team_stats.csv'), index=False)


    def process_team_results_list(self, data):

        results_all = []
        results_home = []
        results_away = []

        score_all = []
        score_home = []
        score_away = []

        concede_all = []
        concede_home = []
        concede_away = []

        data = data.sort_values(by='round')
        data_index = data.index

        data['team_results_all'] = 0
        data['team_results_home'] = 0
        data['team_results_away'] = 0

        data['team_score_all'] = 0
        data['team_score_home'] = 0
        data['team_score_away'] = 0

        data['team_concede_all'] = 0
        data['team_concede_home'] = 0
        data['team_concede_away'] = 0

        data['team_score_all'] = data['team_score_all'].astype('object')
        data['team_score_home'] = data['team_score_home'].astype('object')
        data['team_score_away'] = data['team_score_away'].astype('object')

        data['team_concede_all'] = data['team_concede_all'].astype('object')
        data['team_concede_home'] = data['team_concede_home'].astype('object')
        data['team_concede_away'] = data['team_concede_away'].astype('object')

        data['team_results_all'] = data['team_results_all'].astype('object')
        data['team_results_home'] = data['team_results_home'].astype('object')
        data['team_results_away'] = data['team_results_away'].astype('object')

        data['team_score_all'] = data['team_score_all'].astype('object')
        data['team_score_home'] = data['team_score_home'].astype('object')
        data['team_score_away'] = data['team_score_away'].astype('object')

        data['team_concede_all'] = data['team_concede_all'].astype('object')
        data['team_concede_home'] = data['team_concede_home'].astype('object')
        data['team_concede_away'] = data['team_concede_away'].astype('object')

        for i in range(data.shape[0]):
            index = data_index[i]
            was_home = data['was_home'].iloc[i]
            if data['win'].iloc[i] == 1:
                result_curr = 2
            elif data['draw'].iloc[i] == 1:
                result_curr = 1
            elif data['loss'].iloc[i] == 1:
                result_curr = 0

            score_curr = data['team_score'].iloc[i]
            concede_curr = data['team_concede'].iloc[i]

            results_all.append(result_curr)
            score_all.append(score_curr)
            concede_all.append(concede_curr)

            if was_home == True:
                results_home.append(result_curr)
                score_home.append(score_curr)
                concede_home.append(concede_curr)

            if was_home == False:
                results_away.append(result_curr)
                score_away.append(score_curr)
                concede_away.append(concede_curr)


            data.at[index, 'team_results_all'] = results_all.copy()
            data.at[index,'team_results_home'] = results_home.copy()
            data.at[index,'team_results_away'] = results_away.copy()

            data.at[index, 'team_score_all'] = score_all.copy()
            data.at[index,'team_score_home'] = score_home.copy()
            data.at[index,'team_score_away'] = score_away.copy()

            data.at[index, 'team_concede_all'] = concede_all.copy()
            data.at[index,'team_concede_home'] = concede_home.copy()
            data.at[index,'team_concede_away'] = concede_away.copy()


        return data

    def process_team_results(self, data, results_window=5):

        data = data.sort_values(by='round')
        data_index = data.index


        data['team_prob_win_all_' + str(results_window)] = 0
        data['team_prob_win_home_' + str(results_window)] = 0
        data['team_prob_win_away_' + str(results_window)] = 0

        data['team_prob_draw_all_' + str(results_window)] = 0
        data['team_prob_draw_home_' + str(results_window)] = 0
        data['team_prob_draw_away_' + str(results_window)] = 0

        data['team_prob_loss_all_' + str(results_window)] = 0
        data['team_prob_loss_home_' + str(results_window)] = 0
        data['team_prob_loss_away_' + str(results_window)] = 0

        for i in range(data.shape[0]):

            results_all = data['team_results_all'].iloc[i]
            results_home = data['team_results_home'].iloc[i]
            results_away = data['team_results_away'].iloc[i]

            if len(results_all) >= results_window:
                results_all_np = np.array(results_all[-results_window:].copy())
            else:
                results_all_np = np.array(results_all[:-1].copy())
            if len(results_home) >= results_window:
                results_home_np = np.array(results_home[-results_window:].copy())
            else:
                results_home_np = np.array(results_home[:-1].copy())
            if len(results_away) >= results_window:
                results_away_np = np.array(results_away[-results_window:].copy())
            else:
                results_away_np = np.array(results_away[:-1].copy())

            unknown_prob_all = 0.5
            unknown_prob_home = 0.5
            unknown_prob_away = 0.5

            if results_all_np.shape[0] > 0:
                data['team_prob_win_all_' + str(results_window)].iloc[i] = results_all_np[results_all_np==2].shape[0] / results_all_np.shape[0]
                data['team_prob_draw_all_' + str(results_window)].iloc[i] = results_all_np[results_all_np==1].shape[0] / results_all_np.shape[0]
                data['team_prob_loss_all_' + str(results_window)].iloc[i] = results_all_np[results_all_np==0].shape[0] / results_all_np.shape[0]
            else:
                data['team_prob_win_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_draw_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_loss_all_' + str(results_window)].iloc[i] = unknown_prob_all

            if results_home_np.shape[0] > 0:
                data['team_prob_win_home_' + str(results_window)].iloc[i] = results_home_np[results_home_np==2].shape[0] / results_home_np.shape[0]
                data['team_prob_draw_home_' + str(results_window)].iloc[i] = results_home_np[results_home_np==1].shape[0] / results_home_np.shape[0]
                data['team_prob_loss_home_' + str(results_window)].iloc[i] = results_home_np[results_home_np==0].shape[0] / results_home_np.shape[0]
            else:
                data['team_prob_win_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_draw_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_loss_home_' + str(results_window)].iloc[i] = unknown_prob_home

            if results_away_np.shape[0] > 0:
                data['team_prob_win_away_' + str(results_window)].iloc[i] = results_away_np[results_away_np==2].shape[0] / results_away_np.shape[0]
                data['team_prob_draw_away_' + str(results_window)].iloc[i] = results_away_np[results_away_np==1].shape[0] / results_away_np.shape[0]
                data['team_prob_loss_away_' + str(results_window)].iloc[i] = results_away_np[results_away_np==0].shape[0] / results_away_np.shape[0]
            else:
                data['team_prob_win_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_draw_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_loss_away_' + str(results_window)].iloc[i] = unknown_prob_away

        return data

    def process_team_score(self, data, results_window=5):



        data = data.sort_values(by='round')
        data_index = data.index

        data['team_prob_score_all_' + str(results_window)] = 0
        data['team_prob_score_home_' + str(results_window)] = 0
        data['team_prob_score_away_' + str(results_window)] = 0

        data['team_prob_score2_all_' + str(results_window)] = 0
        data['team_prob_score2_home_' + str(results_window)] = 0
        data['team_prob_score2_away_' + str(results_window)] = 0

        data['team_prob_score3_all_' + str(results_window)] = 0
        data['team_prob_score3_home_' + str(results_window)] = 0
        data['team_prob_score3_away_' + str(results_window)] = 0

        data['team_prob_concede_all_' + str(results_window)] = 0
        data['team_prob_concede_home_' + str(results_window)] = 0
        data['team_prob_concede_away_' + str(results_window)] = 0

        data['team_prob_concede2_all_' + str(results_window)] = 0
        data['team_prob_concede2_home_' + str(results_window)] = 0
        data['team_prob_concede2_away_' + str(results_window)] = 0

        data['team_prob_concede3_all_' + str(results_window)] = 0
        data['team_prob_concede3_home_' + str(results_window)] = 0
        data['team_prob_concede3_away_' + str(results_window)] = 0


        for i in range(data.shape[0]):

            score_all = data['team_score_all'].iloc[i]
            score_home = data['team_score_home'].iloc[i]
            score_away = data['team_score_away'].iloc[i]

            concede_all = data['team_concede_all'].iloc[i]
            concede_home = data['team_concede_home'].iloc[i]
            concede_away = data['team_concede_away'].iloc[i]

            if len(score_all) >= results_window:
                score_all_np = np.array(score_all[-results_window:].copy())
                concede_all_np = np.array(concede_all[-results_window:].copy())
            else:
                score_all_np = np.array(score_all[:-1].copy())
                concede_all_np = np.array(concede_all[:-1].copy())
            if len(score_home) >= results_window+1:
                score_home_np = np.array(score_home[-results_window:].copy())
                concede_home_np = np.array(concede_home[-results_window:].copy())
            else:
                score_home_np = np.array(score_home[:-1].copy())
                concede_home_np = np.array(concede_home[:-1].copy())
            if len(score_away) >= results_window:
                score_away_np = np.array(score_away[-results_window:].copy())
                concede_away_np = np.array(concede_away[-results_window:].copy())
            else:
                score_away_np = np.array(score_away[:-1].copy())
                concede_away_np = np.array(concede_away[:-1].copy())

            unknown_prob_all = 0.5
            unknown_prob_home = 0.5
            unknown_prob_away = 0.5

            if score_all_np.shape[0] > 0:
                data['team_prob_score_all_' + str(results_window)].iloc[i] = score_all_np[score_all_np>0].shape[0] / score_all_np.shape[0]
                data['team_prob_score2_all_' + str(results_window)].iloc[i] = score_all_np[score_all_np>=2].shape[0] / score_all_np.shape[0]
                data['team_prob_score3_all_' + str(results_window)].iloc[i] = score_all_np[score_all_np>=3].shape[0] / score_all_np.shape[0]
            else:
                data['team_prob_score_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_score2_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_score3_all_' + str(results_window)].iloc[i] = unknown_prob_all

            if score_home_np.shape[0] > 0:
                data['team_prob_score_home_' + str(results_window)].iloc[i] = score_home_np[score_home_np>0].shape[0] / score_home_np.shape[0]
                data['team_prob_score2_home_' + str(results_window)].iloc[i] = score_home_np[score_home_np>=2].shape[0] / score_home_np.shape[0]
                data['team_prob_score3_home_' + str(results_window)].iloc[i] = score_home_np[score_home_np>=3].shape[0] / score_home_np.shape[0]
            else:
                data['team_prob_score_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_score2_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_score3_home_' + str(results_window)].iloc[i] = unknown_prob_home

            if score_away_np.shape[0] > 0:
                data['team_prob_score_away_' + str(results_window)].iloc[i] = score_away_np[score_away_np>0].shape[0] / score_away_np.shape[0]
                data['team_prob_score2_away_' + str(results_window)].iloc[i] = score_away_np[score_away_np>=2].shape[0] / score_away_np.shape[0]
                data['team_prob_score3_away_' + str(results_window)].iloc[i] = score_away_np[score_away_np>=3].shape[0] / score_away_np.shape[0]
            else:
                data['team_prob_score_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_score2_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_score3_away_' + str(results_window)].iloc[i] = unknown_prob_away


            if concede_all_np.shape[0] > 0:
                data['team_prob_concede_all_' + str(results_window)].iloc[i] = concede_all_np[concede_all_np>0].shape[0] / concede_all_np.shape[0]
                data['team_prob_concede2_all_' + str(results_window)].iloc[i] = concede_all_np[concede_all_np>=2].shape[0] / concede_all_np.shape[0]
                data['team_prob_concede3_all_' + str(results_window)].iloc[i] = concede_all_np[concede_all_np>=3].shape[0] / concede_all_np.shape[0]
            else:
                data['team_prob_concede_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_concede2_all_' + str(results_window)].iloc[i] = unknown_prob_all
                data['team_prob_concede3_all_' + str(results_window)].iloc[i] = unknown_prob_all

            if concede_home_np.shape[0] > 0:
                data['team_prob_concede_home_' + str(results_window)].iloc[i] = concede_home_np[concede_home_np>0].shape[0] / concede_home_np.shape[0]
                data['team_prob_concede2_home_' + str(results_window)].iloc[i] = concede_home_np[concede_home_np>=2].shape[0] / concede_home_np.shape[0]
                data['team_prob_concede3_home_' + str(results_window)].iloc[i] = concede_home_np[concede_home_np>=3].shape[0] / concede_home_np.shape[0]
            else:
                data['team_prob_concede_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_concede2_home_' + str(results_window)].iloc[i] = unknown_prob_home
                data['team_prob_concede3_home_' + str(results_window)].iloc[i] = unknown_prob_home

            if concede_away_np.shape[0] > 0:
                data['team_prob_concede_away_' + str(results_window)].iloc[i] = concede_away_np[concede_away_np>0].shape[0] / concede_away_np.shape[0]
                data['team_prob_concede2_away_' + str(results_window)].iloc[i] = concede_away_np[concede_away_np>=2].shape[0] / concede_away_np.shape[0]
                data['team_prob_concede3_away_' + str(results_window)].iloc[i] = concede_away_np[concede_away_np>=3].shape[0] / concede_away_np.shape[0]
            else:
                data['team_prob_concede_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_concede2_away_' + str(results_window)].iloc[i] = unknown_prob_away
                data['team_prob_concede3_away_' + str(results_window)].iloc[i] = unknown_prob_away

        return data

    def process_current_game_odds(self, data, results_window=5):



        data['odds_win_' + str(results_window)] = 0
        data['odds_draw_' + str(results_window)] = 0
        data['odds_loss_' + str(results_window)] = 0

        for i in range(data.shape[0]):
            team_id = data['team_unique_id'].iloc[i]
            against_team_id = data['team_unique_id_against'].iloc[i]
            was_home = data['was_home'].iloc[i]

            if was_home == True:
                team_column = 'team_results_home'
                team_against_column = 'team_results_away'
            elif was_home == False:
                team_column = 'team_results_away'
                team_against_column = 'team_results_home'

            team_results = data[data['team_unique_id']==team_id][team_column].values[0]
            team_against_results = data[data['team_unique_id']==against_team_id][team_against_column].values[0]
            if len(team_results) >= results_window+1:
                team_results = np.array(team_results[-results_window-1:-1])
            else:
                team_results = np.array(team_results[:-1])
            if len(team_against_results) >= results_window+1:
                team_against_results = np.array(team_against_results[-results_window-1:-1])
            else:
                team_against_results = np.array(team_against_results[:-1])

            team_wins = team_results[team_results==2].shape[0]
            team_draws = team_results[team_results==1].shape[0]
            team_losses = team_results[team_results==0].shape[0]

            team_against_wins = team_against_results[team_against_results==2].shape[0]
            team_against_draws = team_against_results[team_against_results==1].shape[0]
            team_against_losses = team_against_results[team_against_results==0].shape[0]

            if (team_results.shape[0] + team_against_results.shape[0]) > 0:
                team_odds_win = (team_wins + team_against_losses) / (team_results.shape[0] + team_against_results.shape[0])
                team_odds_draw = (team_draws + team_against_draws) / (team_results.shape[0] + team_against_results.shape[0])
                team_odds_loss = (team_losses + team_against_wins) / (team_results.shape[0] + team_against_results.shape[0])
            elif (team_results.shape[0] + team_against_results.shape[0]) == 0:
                team_odds_win = 1/3
                team_odds_draw = 1/3
                team_odds_loss = 1/3

            data['odds_win_' + str(results_window)].iloc[i] = team_odds_win
            data['odds_draw_' + str(results_window)].iloc[i] = team_odds_draw
            data['odds_loss_' + str(results_window)].iloc[i] = team_odds_loss

        return data


    def process_fixture_odds(self, path_processed,
                             filename_fixture,
                             filename_team_stats,
                             season,
                             results_window=5):

        if season == 2016:
            season_string = '2016-17'
        if season == 2017:
            season_string = '2017-18'
        if season == 2018:
            season_string = '2018-19'
        if season == 2019:
            season_string = '2019-20'
        if season == 2020:
            season_string = '2020-21'


        path_season = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Data', season_string)
        team_stats = pd.read_csv(path.join(path_processed, filename_team_stats))
        fixture_data = pd.read_csv(path.join(path_season, filename_fixture))

        fixture_data['home_odds_win_' + str(results_window)] = 0
        fixture_data['home_odds_draw_' + str(results_window)] = 0
        fixture_data['home_odds_loss_' + str(results_window)] = 0

        fixture_data['away_odds_win_' + str(results_window)] = 0
        fixture_data['away_odds_draw_' + str(results_window)] = 0
        fixture_data['away_odds_loss_' + str(results_window)] = 0

        # event_max = team_stats[team_stats['season']==season]['round'].max()

        for i in range(fixture_data.shape[0]):
            columns = fixture_data.columns

            if 'uniqueid_home' in columns:
                home_team_id = fixture_data['team_home'].iloc[i]
                away_team_id = fixture_data['team_away'].iloc[i]
                event = fixture_data['round'].iloc[i]

            if 'uniqueid_home' not in columns:
                home_team_id = fixture_data['team_h'].iloc[i]
                away_team_id = fixture_data['team_a'].iloc[i]
                event = fixture_data['event'].iloc[i]

            home_team_event_max = team_stats[(team_stats['season']==season) & (team_stats['team_id']==home_team_id)]['round'].max()
            away_team_event_max = team_stats[(team_stats['season']==season) & (team_stats['team_id']==away_team_id)]['round'].max()

            if event >= home_team_event_max:
                home_team_event = home_team_event_max
            else:
                home_team_event = event

            if event >= away_team_event_max:
                away_team_event = away_team_event_max
            else:
                away_team_event = event

            home_team_column = 'team_results_home'
            away_team_column = 'team_results_away'

            if event > 0:
                data_home = team_stats[(team_stats['team_id']==home_team_id) & (team_stats['season']==season) & (team_stats['round']==home_team_event)]
                data_away = team_stats[(team_stats['team_id']==away_team_id) & (team_stats['season']==season) & (team_stats['round']==away_team_event)]

                if data_home.shape[0] > 0 and data_away.shape[0] > 0:
                    home_results = json.loads(data_home[home_team_column].values[0])

                    if len(home_results) >= results_window+1:
                        home_results = np.array(home_results[-results_window-1:-1])
                    else:
                        home_results = np.array(home_results[:-1])

                    away_results = json.loads(data_away[away_team_column].values[0])
                    if len(away_results) >= results_window+1:
                        away_results = np.array(away_results[-results_window-1:-1])
                    else:
                        away_results = np.array(away_results[:-1])

                    home_wins = home_results[home_results==2].shape[0]
                    home_draws = home_results[home_results==1].shape[0]
                    home_losses = home_results[home_results==0].shape[0]

                    away_wins = away_results[away_results==2].shape[0]
                    away_draws = away_results[away_results==1].shape[0]
                    away_losses = away_results[away_results==0].shape[0]

                    if (home_results.shape[0] + away_results.shape[0]) > 0:
                        home_odds_win = (home_wins + away_losses) / (home_results.shape[0] + away_results.shape[0])
                        home_odds_draw = (home_draws + away_draws) / (home_results.shape[0] + away_results.shape[0])
                        home_odds_loss = (home_losses + away_wins) / (home_results.shape[0] + away_results.shape[0])
                    elif (home_results.shape[0] + away_results.shape[0]) == 0:
                        home_odds_win = 1/3
                        home_odds_draw = 1/3
                        home_odds_loss = 1/3

                    fixture_data['home_odds_win_' + str(results_window)].iloc[i] = home_odds_win
                    fixture_data['home_odds_draw_' + str(results_window)].iloc[i] = home_odds_draw
                    fixture_data['home_odds_loss_' + str(results_window)].iloc[i] = home_odds_loss

                    fixture_data['away_odds_win_' + str(results_window)].iloc[i] = home_odds_loss
                    fixture_data['away_odds_draw_' + str(results_window)].iloc[i] = home_odds_draw
                    fixture_data['away_odds_loss_' + str(results_window)].iloc[i] = home_odds_win

        fixture_data.to_csv(path.join(path_season, filename_fixture), index=False)


    def odds(self):
        pass

    def form(self):
        pass




