import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import os.path as path
import dash_table
import DataLoader as DL
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests


def find_unique_id(data, first_name, second_name, season):
    """

    :param data:
    :param first_name:
    :param second_name:
    :param season:
    :return:
    """

    name = first_name + '_' + second_name
    data_filt = data[data['season'] == season]
    data_filt = data_filt[data_filt['name'] == name]
    return data_filt['unique_id'].iloc[0]


def find_top_results(data, target_column, n, element_type=-1):
    """mean_total_points_any_all

    :param data:
    :param target_column:
    :param n:
    :param element_type:
    :return:
    """

    data_filt = data.copy()
    if element_type > 0:
        data_filt = data_filt[data_filt['element_type']==element_type]

    data_filt = data_filt[data_filt['round']==data_filt['round'].max()]
    data_filt = data_filt.sort_values(by=target_column, ascending=False)

    return data_filt['unique_id'].iloc[:n]

def postion2element_type(position):
    """

    :param position:
    :return:
    """

    element_type = -1

    if position == 'Goalkeeper':
        element_type = 1
    elif position == 'Defender':
        element_type = 2
    elif position == 'Midfielder':
        element_type = 3
    elif position == 'Striker':
        element_type = 4

    return element_type

def element_type2position(element_type):
    """

    :param position:
    :return:
    """
    if element_type == 1:
        position = 'GKP'
    elif element_type == 2:
        position = 'DEF'
    elif element_type == 3:
        position = 'MID'
    elif element_type == 4:
        position = 'FWD'

    return position


def determine_element_id(data, unique_id, season):

    return data[(data['season']==season) & (data['unique_id']==unique_id)]['element'].unique()[0]

def determine_unique_id(data, element_id, season):

    return int(data[(data['season']==season) & (data['element']==element_id)]['unique_id'].unique()[0])


def determine_player_form(data, unique_id):

    max_round = data[data['unique_id']==unique_id]['round'].max()

    return data[(data['unique_id']==unique_id) & (data['round']==max_round)]['mean_total_points_any_4'].values[0]


def determine_player_team_unique_id(data, unique_id):

    max_round = data[data['unique_id']==unique_id]['round'].max()

    return data[(data['unique_id']==unique_id) & (data['round']==max_round)]['team_unique_id'].values[0]

def determine_player_position(data, unique_id):

    element_type = data[data['unique_id']==unique_id]['element_type'].unique()[-1]

    return element_type2position(element_type)

def determine_player_name(data, unique_id):

    player_name = data[data['unique_id']==unique_id]['name'].values[0]

    return player_name

def determine_player_team_code(team_codes, team_unique_id):

    team_code = team_codes[team_codes['team_unique_id']==team_unique_id]['code'].unique()[-1]

    return team_code

def determine_player_team_code_id(team_codes, team_id):

    team_code = team_codes[(team_codes['team_id']==team_id) & (team_codes['season']==season_latest)]['code'].values[0]

    return team_code

def determine_player_team_id(team_codes, team_unique_id):

    team_id = team_codes[team_codes['team_unique_id']==team_unique_id]['team_id'].values[-1]

    return team_id

def determine_player_fixtures(fixture_data, team_codes, team_id, round_next):

    fixture_data = fixture_data[fixture_data['event']==round_next]
    fixtures_team = fixture_data[(fixture_data['team_h']==team_id) | (fixture_data['team_a']==team_id)]
    # print(fixtures_team['team_h'])

    was_home = []
    opposition = []
    odds_win = []
    fixture_diff = []

    if fixtures_team.shape[0] > 0:
        for i in range(fixtures_team.shape[0]):
            if fixtures_team['team_h'].iloc[i] == team_id:
                was_home.append('H')
                opposition.append(determine_player_team_code_id(team_codes, fixtures_team['team_a'].iloc[i]))
                odds_win.append('{0:.2f}'.format(fixtures_team['home_odds_win_4'].iloc[i]))
                fixture_diff.append(fixtures_team['team_h_difficulty'].iloc[i])
            else:
                was_home.append('A')
                opposition.append(determine_player_team_code_id(team_codes, fixtures_team['team_h'].iloc[i]))
                odds_win.append('{0:.2f}'.format(fixtures_team['away_odds_win_4'].iloc[i]))
                fixture_diff.append(fixtures_team['team_a_difficulty'].iloc[i])


    if len(was_home) == 0:
        was_home.append('-')
        was_home.append('-')
        opposition.append('-')
        opposition.append('-')
        odds_win.append('-')
        odds_win.append('-')
        fixture_diff.append(0)
        fixture_diff.append(0)
    elif len(was_home) == 1:
        was_home.append('-')
        opposition.append('-')
        odds_win.append('-')
        fixture_diff.append(0)

    return opposition, was_home, odds_win, fixture_diff


def planner_process_player(data, team_codes, fixture_data, element_id, season, round_next):
    unique_id = determine_unique_id(data, element_id, season)
    player_form = '{0:.2f}'.format(determine_player_form(data, unique_id))
    team_unique_id = determine_player_team_unique_id(data, unique_id)
    team_id = determine_player_team_id(team_codes, team_unique_id)
    player_position = determine_player_position(data, unique_id)
    team_code = determine_player_team_code(team_codes, team_unique_id)
    player_name = determine_player_name(data, unique_id)
    opposition, was_home, odds_win, fixture_diff = determine_player_fixtures(fixture_data, team_codes, team_id, round_next)
    player_form_list = []

    if opposition[0] == '-':
        player_form_list.append('-')
        player_form_list.append('-')
        n_matches = 0
    elif opposition[0] != '-' and opposition[1] == '-':
        player_form_list.append(player_form)
        player_form_list.append('-')
        n_matches = 1
    else:
        player_form_list.append(player_form)
        player_form_list.append(player_form)
        n_matches = 2

    return unique_id, player_form_list, team_unique_id, team_id, player_position, team_code, player_name, opposition, was_home, odds_win, fixture_diff, n_matches

def create_player_div(i, team_unique_ids, team_names, team_picks, data, team_codes, fixture_data, season_latest, round_curr, font_size, round_id):

    round_process = round_curr + round_id
    player_id = team_picks['element'].iloc[i]
    player_captain = team_picks['is_captain'].iloc[i]
    if player_captain == True:
        captain_value = 'CPT'
    else:
        captain_value = ''
    player_value = '{0:.1f}'.format(team_picks['selling_price'].iloc[i]/10)
    (player_unique_id, player_form, player_team_unique_id, player_team_id, player_position, player_team_code, player_player_name, player_opposition, player_was_home, player_odds_win, fixture_diff, n_matches) = \
        planner_process_player(data, team_codes, fixture_data, player_id, season_latest, round_process)

    colour_codes = ['white', 'darkgreen', 'palegreen', 'yellow', 'orange', 'red']

    player_no = i + 1

    match_1 = html.Div([
        html.Div(children=str(player_no)+'.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_position, id='player_'+str(round_id)+'_'+str(player_no)+'_1_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(dcc.Dropdown(
                    id='player_'+str(round_id)+'_'+str(player_no)+'_name',
                    options=[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)],
                    value=player_unique_id,
                    multi=False),
                style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
        html.Div(children=player_value, id='player_'+str(round_id)+'_'+str(player_no)+'_1_value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_team_code, id='player_'+str(round_id)+'_'+str(player_no)+'_1_team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        # html.Div(children=player_opposition[0], id='player_'+str(round_id)+'_'+str(player_no)+'_1_against', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'background-color': fixture_diff_colour(fixture_diff[0])}),
        html.Div(children=player_opposition[0], id='player_'+str(round_id)+'_'+str(player_no)+'_1_against', style=player_opposition_style(font_size, fixture_diff[0])),
        html.Div(children=player_was_home[0], id='player_'+str(round_id)+'_'+str(player_no)+'_1_H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_form[0], id='player_'+str(round_id)+'_'+str(player_no)+'_1_player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children='-', id='player_'+str(round_id)+'_'+str(player_no)+'_1_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_odds_win[0], id='player_'+str(round_id)+'_'+str(player_no)+'_1_team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(
            dcc.Checklist(
                options=[
                    {'label': '', 'value': 'CPT'},
                ],
            value=[captain_value],
            style={'float': 'center'},
            id='player_'+str(round_id)+'_'+str(player_no)+'_cpt')
        , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

        html.Div(
            dcc.Checklist(
                options=[
                    {'label': '', 'value': 'TRN'},
                ],
            style={'float': 'center'},
            id='player_'+str(round_id)+'_'+str(player_no)+'_transfer')
        , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

    ], style={'width': '100%','float': 'left'}),

    # print(match_1)

    # if n_matches == 2:
    #     # Player 1, 2nd game placeholder
    #     match_2 = html.Div([
    #         html.Div(children=str(player_no)+'.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
    #         html.Div(children=player_position, id='player_'+str(round_id)+'_'+str(player_no)+'_2_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
    #         html.Div(children='XXXXXXXXXX', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'color': 'white'}),
    #         html.Div(children='X.X', id='player_'+str(round_id)+'_'+str(player_no)+'_2_value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
    #         html.Div(children='XXX', id='player_'+str(round_id)+'_'+str(player_no)+'_2_team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
    #         html.Div(children=player_opposition[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_against', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children=player_was_home[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children=player_form[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children='-', id='player_'+str(round_id)+'_'+str(player_no)+'_2_team_form_l2', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children=player_odds_win[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children='', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
    #         html.Div(children='',style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})
    #
    #     ], style={'width': '100%','float': 'left'}),
    # else:
    #     match_2 = [None]

    # Player 1, 2nd game placeholder
    match_2 = html.Div([
        html.Div(children=str(player_no)+'.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children=player_position, id='player_'+str(round_id)+'_'+str(player_no)+'_2_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='XXXXXXXXXX', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'color': 'white'}),
        html.Div(children='X.X', id='player_'+str(round_id)+'_'+str(player_no)+'_2_value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='XXX', id='player_'+str(round_id)+'_'+str(player_no)+'_2_team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        # html.Div(children=player_opposition[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_against', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'background-color': fixture_diff_colour(fixture_diff[1])}),
        html.Div(children=player_opposition[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_against', style=player_opposition_style(font_size, fixture_diff[1])),
        html.Div(children=player_was_home[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_form[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children='-', id='player_'+str(round_id)+'_'+str(player_no)+'_2_team_form_l2', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children=player_odds_win[1], id='player_'+str(round_id)+'_'+str(player_no)+'_2_team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children='', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
        html.Div(children='',style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

    ], style={'width': '100%','float': 'left'}),

    # Blank Line
    blank = html.Div([
        html.Div(children='1.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children=player_position, style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='XXXXXXXXXX', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'color': 'white'}),
        html.Div(children='X.X', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='XXX', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='WBA', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children=player_form[0], style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='5.0', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='10/1', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'}),
        html.Div(children='',style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'color': 'white'})

    ], style={'width': '100%','float': 'left'}),

    return match_1, match_2, blank


def fixture_diff_colour(fixture_diff):
    colour_names = ['white', 'darkgreen', 'palegreen', 'yellow', 'orange', 'red']

    # print(fixture_diff, colour_names[fixture_diff])
    return colour_names[fixture_diff]

def player_opposition_style(font_size, fixture_diff):

    style = {'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'background-color': fixture_diff_colour(fixture_diff)}

    return style

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

########################################
####### Load Data ######################
########################################

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_database.csv')
path_player_metadata = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_metadata.csv')
path_team_metadata = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'team_metadata.csv')
path_team_codes = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'team_codes.csv')

data = pd.read_csv(path_data)
player_metadata = pd.read_csv(path_player_metadata)
team_metadata = pd.read_csv(path_team_metadata)
team_codes = pd.read_csv(path_team_codes)
fixture_data = pd.read_csv('/home/john/Documents/projects/fpl-analystics-prediction/Data/2020-21/fixtures.csv')

data['mean_total_points_any_3/pound'] = data['mean_total_points_any_3'] / (data['value'] / 10)
data['mean_total_points_any_5/pound'] = data['mean_total_points_any_5'] / (data['value'] / 10)
data['total_total_points_any_all/pound'] = data['total_total_points_any_all'] / (data['value'] / 10)
data['name_first'] = data['name'].str.split('_', expand=True)[0]
data['name_last'] = data['name'].str.split('_', expand=True)[1].str.slice(start=0, stop=20)

path_league_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_standings_full.csv')
path_league_data_full = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_data_full.csv')
available_indicators = data.columns

DataLoaderObj = DL.DataLoader()
DataLoaderObj.scrape_league_standings(path_league_data_full,
                                      path_league_data,
                                      league_id=1218670,
                                      league_type='classic')

data_team_ids_summary = pd.read_csv(path_league_data, encoding='UTF-8')
data_team_ids_summary = data_team_ids_summary.rename(columns={"id": "identifier", "entry": "id"})
data_team_ids = data_team_ids_summary.copy()
data_team_ids = data_team_ids[['rank', 'entry_name', 'total']]
data_league_standings = pd.read_csv(path_league_data_full, encoding='UTF-8')

data_league_standings = data_league_standings.merge(data_team_ids_summary.drop(columns=['rank', 'rank_sort']), on=['id'])
labels_league_standings = data_league_standings.columns

league_ids = ['1217918', '1218670']
league_names = ['The league of Leith', 'The old office Vs no AI']

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    dcc.Tabs(id='tabs-example', value='Planner', children=[
        dcc.Tab(label='Aggregate Player Analysis', value='APA'),
        dcc.Tab(label='Individual Player Analysis', value='IPL'),
        dcc.Tab(label='FPL League Analysis', value='LA'),
        dcc.Tab(label='Planner', value='Planner'),
    ]),
    html.Div(id='tabs-example-content'),
])


# Get list of player names and associated unique id's

# season_latest = player_metadata['season'].max()
season_latest = 2020
player_metadata_season = player_metadata[player_metadata['season'] == season_latest]
round_curr = 17
round_next = round_curr + 1

player_names = []
unique_ids = []

for i in range(player_metadata_season.shape[0]):
    player_name_key = player_metadata_season['name'].iloc[i]
    player_name = player_metadata_season['name_first'].iloc[i] + ' ' + player_metadata_season['name_last'].iloc[i]
    unique_id = player_metadata_season['unique_id'].iloc[i]
    player_names.append(player_name)
    unique_ids.append(unique_id)

players_2020_names_json = pd.Series(data[data['season']==season_latest]['name'].unique()).to_json(date_format='iso', orient='split')
players_2020_unique_ids_json = pd.Series(data[data['season']==season_latest]['unique_id'].unique()).to_json(date_format='iso', orient='split')

font_size = '10px'

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
def render_content(tab):
    if tab == 'APA':
        return (html.Div([

            html.Div([
                html.Div(children='''
                    Choose the player position to display:
                '''),

                dcc.RadioItems(
                    id='position-type',
                    options=[{'label': i, 'value': i} for i in ['All', 'Goalkeeper', 'Defender', 'Midfielder', 'Striker']],
                    value='All'),

                html.Div(children='''
                    Choose the season to use:
                '''),

                dcc.Dropdown(
                    id='year-filter',
                    options=[{'label': i, 'value': i} for i in data['season'].unique()],
                    value=data['season'].unique().max(),
                    multi=False),

            ], style={'width': '48%', 'display': 'inline-block'}),


            html.Div([
                html.Div([
                    html.Div(children='''
                        Choose players to display:
                    '''),

                    dcc.RadioItems(
                        id='player-selection-type',
                        options=[{'label': i, 'value': i} for i in ['Top players', 'Manual']],
                        value='Top players'),

                    html.Div(children='''
                        Select the players to display:
                    '''),

                    dcc.Dropdown(
                        id='player-filter',
                        options=[{'label': i, 'value': i} for i in data.sort_values(by='name_last')[data['season']==season_latest]['name'].unique()],
                        multi=True),
                ], style={'padding': '1%'}),

                html.Div([
                    html.Div([
                        html.Div(children='''
                            No. players to display:
                        '''),

                        dcc.Input(
                            id='n',
                            value='10')
                    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            Aggregate:
                        '''),
                        dcc.Dropdown(
                            id='fig-aggregate-column',
                            options=[{'label': i, 'value': i} for i in available_indicators],
                            value='mean_total_points_any_3')
                    ], style={'width': '48%', 'float': 'left', 'display': 'inline-block'}),
                ]),


            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        ], style={'padding-bottom': '1%'}),

        # Figure 1 - Aggregate based plot
        html.Div([
            dcc.Graph(id='fig1-aggregate-graph'),

            html.Div([
                html.Div(children='''
                    x-data:
                '''),

                dcc.Dropdown(
                    id='fig1-xaxis-column',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='name_last')
                ], style={'width': '22%', 'display': 'inline-block'}),

            html.Div([
                html.Div(children='''
                    y-data:
                '''),
                dcc.Dropdown(
                    id='fig1-yaxis-column',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='mean_total_points_any_3')
                ], style={'width': '22%', 'float': 'center', 'display': 'inline-block'}),

            html.Div([
                html.Div(children='''
                    Error bars:
                '''),
                dcc.Dropdown(
                    id='fig1-errorbar-column',
                    options=[{'label': i, 'value': i} for i in ['Standard Deviation', 'Standard Error']],
                    value='Standard Error')
                ], style={'width': '22%', 'float': 'center', 'display': 'inline-block', 'padding_bottom': '3%'}),

            html.Div([
                html.Div(children='''
                    Choose the plot type::
                '''),
                dcc.Dropdown(
                    id='fig1-plot-type',
                    options=[{'label': i, 'value': i} for i in ['Bar', 'Box']],
                    value='Bar')
                ], style={'width': '22%', 'float': 'right', 'display': 'inline-block', 'padding_bottom': '3%'}),

            # Hidden div inside the app that stores the intermediate value
            html.Div(id='unique_id_clickData', style={'display': 'none'})

        ], style={'padding_bottom': '10%'}),

        # Create grid of plots showing
        # Figure 2 - Time based plot
        html.Div([
            html.Div([
                dcc.Graph(id='fig2-points-graph'),

                html.Div([
                    html.Div(children='''
                        y-data:
                    '''),
                    dcc.Dropdown(
                        id='fig2-points-yaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='total_points')
                    ], style={'width': '50%', 'float': 'center', 'display': 'inline-block', 'padding-left': '25%'}),

            ], style={'width': '31%', 'float': 'left', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(id='fig2-goals-graph'),

                html.Div([
                    html.Div(children='''
                        y-data:
                    '''),
                    dcc.Dropdown(
                        id='fig2-goals-yaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='goals_scored')
                    ], style={'width': '50%', 'float': 'center', 'display': 'inline-block', 'padding-left': '25%'}),

            ], style={'width': '31%', 'float': 'left', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(id='fig2-assists-graph'),

                html.Div([
                    html.Div(children='''
                        y-data:
                    '''),
                    dcc.Dropdown(
                        id='fig2-assists-yaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='assists')
                    ], style={'width': '50%', 'float': 'center', 'display': 'inline-block', 'padding-left': '25%'}),

            ], style={'width': '31%', 'float': 'left', 'display': 'inline-block'}),
        ]))
    elif tab == 'LA':
        return (html.Div([

            html.Div([
                html.Div(
                    children='''
                    Select League ID here:
                '''),
                dcc.Dropdown(
                    id='input-league_id',
                    options=[{'label': league_names[i], 'value': league_ids[i]} for i in range(len(league_names))],
                    value='1217918',
                ),

            ], style={'width': '22%', 'float': 'center', 'display': 'inline-block', 'padding-bottom': '2%'}),

            html.Div([

                html.Div([

                    html.Div(
                        children='''
                        Current league table:
                    ''', style={'padding-bottom': '2%'}),

                    html.Div(
                        dash_table.DataTable(
                            id='table_league',
                            columns=[{"name": i, "id": i} for i in data_team_ids.columns],
                            data=data_team_ids.to_dict('records')),
                        style={'padding-bottom': '4%'}),

                    html.Div(
                        children='''
                        Team strength:
                    ''', style={'padding-bottom': '2%'}),

                    dash_table.DataTable(
                        id='table_league',
                        columns=[{"name": i, "id": i} for i in data_team_ids.columns],
                        data=data_team_ids.to_dict('records')),

                    ], style={'width': '45%', 'float': 'left', 'display': 'inline-block'}),

                html.Div([
                    html.Div([
                        dcc.Graph(id='fig-league_graph'),

                    html.Div([
                        html.Div(children='''
                            x-data:
                        '''),

                        dcc.Dropdown(
                            id='fig1-xaxis-column',
                            options=[{'label': i, 'value': i} for i in labels_league_standings],
                            value='round')
                        ], style={'width': '48%', 'float': 'center', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            y-data:
                        '''),
                        dcc.Dropdown(
                            id='fig1-yaxis-column',
                            options=[{'label': i, 'value': i} for i in labels_league_standings],
                            value='total_points')
                        ], style={'width': '48%', 'float': 'center', 'display': 'inline-block'}),

                    ]),
                ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            ]),

        ])
        )
    elif tab == 'IPL':
        return (html.Div([
            # Column 1 - Player form indicators
            html.Div([
                html.Div(
                        children='''
                        Player Data:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    html.Div([

                        html.Div([
                            html.Div('''Player Name: ''', style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),
                            html.Div(dcc.Dropdown(
                                id='IPL_playerselect',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=2327,
                                # value=2828,
                                multi=False),
                            style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
                        ]),

                        html.Div([
                            html.Div('''Reference Player: ''', style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),
                            html.Div(dcc.Dropdown(
                                id='IPL_reference_player',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                # value=2828,
                                value=2327,
                                multi=False),
                            style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
                        ]),

                        html.Div([
                            html.Div('''Position: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''FWD ''', id='IPL_position', style={'width': '25%', 'display': 'inline-block'}),
                            html.Div('''GKP ''', id='IPL_position_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Team: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''Leeds Utd. ''', id='IPL_team', style={'width': '25%', 'display': 'inline-block'}),
                            html.Div('''Leeds Utd. ''', id='IPL_team_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Cost: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''6.5M ''', id='IPL_value', style={'width': '25%', 'display': 'inline-block'}),
                            html.Div('''6.5M ''', id='IPL_value_reference', style={'width': '25%', 'display': 'inline-block'}),

                        ]),

                        html.Div([
                            html.Div('''Selected: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_selected', style={'width': '25%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_selected_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Fitness to play: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_FTP', style={'width': '25%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_FTP_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''News: ''', style={'width': '35%', 'display': 'inline-block'}),
                            html.Div('''''', id='IPL_news', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''News (Reference): ''', style={'width': '35%', 'display': 'inline-block'}),
                            html.Div('''''', id='IPL_news_reference', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
                        ]),



                    ], style={'width': '70%','float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(id='IPL_player_picture',style={'width': '90%'})

                    ], style={'width': '23%', 'float': 'right', 'display': 'inline-block'})

                ], style={'width': '98%', 'display': 'inline-block'}),

                # Player Form
                html.Div(
                        children='''
                        Player Form:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    dcc.Graph(id='IPA_indicator_form'),

                ], style={'padding-bottom': '3%'}),

                # Total points
                html.Div(
                        children='''
                        Total Points:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    dcc.Graph(id='IPA_indicator_totalpoints'),


                ], style={'padding-bottom': '3%'}),


                # ICT Index
                html.Div(
                        children='''
                        ICT Index:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    dcc.Graph(id='IPA_indicator_ICT'),

                ], style={'padding-bottom': '3%'}),

                # Probabilities
                html.Div(
                        children='''
                        Probabilities:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    dcc.Graph(id='IPA_indicator_prob'),


                ], style={'padding-bottom': '3%'}),

                # Histogram
                html.Div(
                        children='''
                        Histogram of total points:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    dcc.Graph(id='IPL_histogram'),

                ], style={'padding-bottom': '3%'}),


                ], style={'width': '33%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            # Column 2
            html.Div([
                # box 1 - Fixture information
                html.Div([
                    html.Div(
                            children='''
                            Fixture Information:
                        ''', style={'font-size': '30px'}),
                    ], style={'width': '100%', 'float': 'left', "border":"2px black solid"}),

                # box 2 - Player graphs
                html.Div([
                    html.Div([
                        html.Div(
                                children='''
                                Player Graphs:
                            ''', style={'font-size': '30px'}),

                    ]),

                    html.Div([
                        dcc.Graph(id='IPL_round_subplots'),

                    ], style={'padding-bottom': '3%'}),


                ], style={'width': '100%', 'float': 'left', "border":"2px black solid"}),




                ],style={'width': '66%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),
            ])
        )
    elif tab == 'Planner':

        email = 'speeder1987@gmail.com'
        password = 'Footb@ll2020'
        team_id = '5403039'
        team_picks = DataLoaderObj.scrape_team_information(email, password, team_id)
        team_picks_json = team_picks.to_json(date_format='iso', orient='split')

        player_1_id = team_picks['element'].iloc[0]
        player_1_captain = team_picks['is_captain'].iloc[0]
        player_1_value = '{0:.1f}'.format(team_picks['selling_price'].iloc[0]/10)
        (player_1_unique_id, player_1_player_form, player_1_team_unique_id, player_1_team_id, player_1_position, player_1_team_code, player_1_player_name, player_1_opposition, player_1_was_home, player_1_odds_win, player_1_fixture_diff, n_matches) = \
            planner_process_player(data, team_codes, fixture_data, player_1_id, season_latest, round_next)


        player_2_id = team_picks['element'].iloc[1]
        player_2_captain = team_picks['is_captain'].iloc[1]
        player_2_unique_id, player_2_player_form, player_2_team_unique_id, player_2_team_id, player_2_position, player_2_team_code, player_2_player_name, player_2_opposition, player_2_was_home, player_2_odds_win, player_2_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_2_id, season_latest, round_next)


        player_3_id = team_picks['element'].iloc[2]
        player_3_captain = team_picks['is_captain'].iloc[2]
        player_3_unique_id, player_3_player_form, player_3_team_unique_id, player_3_team_id, player_3_position, player_3_team_code, player_3_player_name, player_3_opposition, player_3_was_home, player_3_odds_win, player_3_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_3_id, season_latest, round_next)

        player_4_id = team_picks['element'].iloc[3]
        player_4_captain = team_picks['is_captain'].iloc[3]
        player_4_unique_id, player_4_player_form, player_4_team_unique_id, player_4_team_id, player_4_position, player_4_team_code, player_4_player_name, player_4_opposition, player_4_was_home, player_4_odds_win, player_4_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_4_id, season_latest, round_next)

        player_5_id = team_picks['element'].iloc[4]
        player_5_captain = team_picks['is_captain'].iloc[4]
        player_5_unique_id, player_5_player_form, player_5_team_unique_id, player_5_team_id, player_5_position, player_5_team_code, player_5_player_name, player_5_opposition, player_5_was_home, player_5_odds_win, player_5_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_5_id, season_latest, round_next)

        player_6_id = team_picks['element'].iloc[5]
        player_6_captain = team_picks['is_captain'].iloc[5]
        player_6_unique_id, player_6_player_form, player_6_team_unique_id, player_6_team_id, player_6_position, player_6_team_code, player_6_player_name, player_6_opposition, player_6_was_home, player_6_odds_win, player_6_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_6_id, season_latest, round_next)


        player_7_id = team_picks['element'].iloc[6]
        player_7_captain = team_picks['is_captain'].iloc[6]
        player_7_unique_id, player_7_player_form, player_7_team_unique_id, player_7_team_id, player_7_position, player_7_team_code, player_7_player_name, player_7_opposition, player_7_was_home, player_7_odds_win, player_7_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_7_id, season_latest, round_next)


        player_8_id = team_picks['element'].iloc[7]
        player_8_captain = team_picks['is_captain'].iloc[7]
        player_8_unique_id, player_8_player_form, player_8_team_unique_id, player_8_team_id, player_8_position, player_8_team_code, player_8_player_name, player_8_opposition, player_8_was_home, player_8_odds_win, player_8_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_8_id, season_latest, round_next)


        player_9_id = team_picks['element'].iloc[8]
        player_9_captain = team_picks['is_captain'].iloc[8]
        player_9_unique_id, player_9_player_form, player_9_team_unique_id, player_9_team_id, player_9_position, player_9_team_code, player_9_player_name, player_9_opposition, player_9_was_home, player_9_odds_win, player_9_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_9_id, season_latest, round_next)


        player_10_id = team_picks['element'].iloc[9]
        player_10_captain = team_picks['is_captain'].iloc[9]
        player_10_unique_id, player_10_player_form, player_10_team_unique_id, player_10_team_id, player_10_position, player_10_team_code, player_10_player_name, player_10_opposition, player_10_was_home, player_10_odds_win, player_10_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_10_id, season_latest, round_next)

        player_11_id = team_picks['element'].iloc[10]
        player_11_captain = team_picks['is_captain'].iloc[10]
        player_11_unique_id, player_11_player_form, player_11_team_unique_id, player_11_team_id, player_11_position, player_11_team_code, player_11_player_name, player_11_opposition, player_11_was_home, player_11_odds_win, player_11_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_11_id, season_latest, round_next)

        player_s1_id = team_picks['element'].iloc[11]
        player_s1_captain = team_picks['is_captain'].iloc[11]
        player_s1_unique_id, player_s1_player_form, player_s1_team_unique_id, player_s1_team_id, player_s1_position, player_s1_team_code, player_s1_player_name, player_s1_opposition, player_s1_was_home, player_s1_odds_win, player_s1_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_s1_id, season_latest, round_next)

        player_s2_id = team_picks['element'].iloc[12]
        player_s2_captain = team_picks['is_captain'].iloc[12]
        player_s2_unique_id, player_s2_player_form, player_s2_team_unique_id, player_s2_team_id, player_s2_position, player_s2_team_code, player_s2_player_name, player_s2_opposition, player_s2_was_home, player_s2_odds_win, player_s2_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_s2_id, season_latest, round_next)

        player_s3_id = team_picks['element'].iloc[13]
        player_s3_captain = team_picks['is_captain'].iloc[13]
        player_s3_unique_id, player_s3_player_form, player_s3_team_unique_id, player_s3_team_id, player_s3_position, player_s3_team_code, player_s3_player_name, player_s3_opposition, player_s3_was_home, player_s3_odds_win, player_s3_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_s3_id, season_latest, round_next)

        player_s4_id = team_picks['element'].iloc[14]
        player_s4_captain = team_picks['is_captain'].iloc[14]
        player_s4_unique_id, player_s4_player_form, player_s4_team_unique_id, player_s4_team_id, player_s4_position, player_s4_team_code, player_s4_player_name, player_a4_opposition, player_s4_was_home, player_s4_odds_win, player_s4_fixture_diff, n_matches = \
            planner_process_player(data, team_codes, fixture_data, player_s4_id, season_latest, round_next)

        team_names = [player_1_player_name,
                      player_2_player_name,
                      player_3_player_name,
                      player_4_player_name,
                      player_5_player_name,
                      player_6_player_name,
                      player_7_player_name,
                      player_8_player_name,
                      player_9_player_name,
                      player_10_player_name,
                      player_11_player_name,
                      player_s1_player_name,
                      player_s2_player_name,
                      player_s3_player_name,
                      player_s4_player_name]

        team_names_df = pd.Series(team_names)
        team_names_json = team_names_df.to_json(date_format='iso', orient='split')

        team_unique_ids = [player_1_unique_id,
                           player_2_unique_id,
                           player_3_unique_id,
                           player_4_unique_id,
                           player_5_unique_id,
                           player_6_unique_id,
                           player_7_unique_id,
                           player_8_unique_id,
                           player_9_unique_id,
                           player_10_unique_id,
                           player_11_unique_id,
                           player_s1_unique_id,
                           player_s2_unique_id,
                           player_s3_unique_id,
                           player_s4_unique_id]

        team_unique_ids_df = pd.Series(team_unique_ids)
        team_unique_ids_json = team_unique_ids_df.to_json(date_format='iso', orient='split')


        #Column 1 (GW+1)
        player_1_X_1 = []
        player_1_X_2 = []
        blanks_1 = []

        round_id = 1
        for i in range(0, len(team_names)):
            player_1_1_div, player_1_2_div, blank = create_player_div(i, team_unique_ids, team_names, team_picks, data, team_codes, fixture_data, season_latest, round_curr, font_size, round_id)
            player_1_X_1.append(player_1_1_div)
            player_1_X_2.append(player_1_2_div)
            blanks_1.append(blank)


        #Column 2 (GW+2)
        player_2_X_1 = []
        player_2_X_2 = []
        blanks_2 = []

        round_id = 2
        for i in range(0, len(team_names)):
            player_2_1_div, player_2_2_div, blank = create_player_div(i, team_unique_ids, team_names, team_picks, data, team_codes, fixture_data, season_latest, round_curr, font_size, round_id)
            player_2_X_1.append(player_2_1_div)
            player_2_X_2.append(player_2_2_div)
            blanks_2.append(blank)


        #Column 3 (GW+3)
        player_3_X_1 = []
        player_3_X_2 = []
        blanks_3 = []

        round_id = 3
        for i in range(0, len(team_names)):
            player_3_1_div, player_3_2_div, blank = create_player_div(i, team_unique_ids, team_names, team_picks, data, team_codes, fixture_data, season_latest, round_curr, font_size, round_id)
            player_3_X_1.append(player_3_1_div)
            player_3_X_2.append(player_3_2_div)
            blanks_3.append(blank)


        #Column 4 (GW+4)
        player_4_X_1 = []
        player_4_X_2 = []
        blanks_4 = []

        round_id = 4
        for i in range(0, len(team_names)):
            player_4_1_div, player_4_2_div, blank = create_player_div(i, team_unique_ids, team_names, team_picks, data, team_codes, fixture_data, season_latest, round_curr, font_size, round_id)
            player_4_X_1.append(player_4_1_div)
            player_4_X_2.append(player_4_2_div)
            blanks_4.append(blank)



        return (
            html.Div([html.Div([
                html.Div(children='GW+1'),

                html.Div([
                    html.Div(children='No.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Pos', id='pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Name', id='name', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Value (£)', id='Value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team', id='team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Agst.', id='Agst.', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Home/ Away', id='H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Player Form', id='player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team Form', id='team_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Odds (win)', id='team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Cpt.', id='captain', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Trn.', id='transfer', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),

                ], style={'width': '100%','float': 'left'}),

                player_1_X_1[0][0],
                player_1_X_2[0][0],
                blanks_1[0][0],

                player_1_X_1[1][0],
                player_1_X_2[1][0],
                blanks_1[1][0],

                player_1_X_1[2][0],
                player_1_X_2[2][0],
                blanks_1[2][0],

                player_1_X_1[3][0],
                player_1_X_2[3][0],
                blanks_1[3][0],

                player_1_X_1[4][0],
                player_1_X_2[4][0],
                blanks_1[4][0],

                player_1_X_1[5][0],
                player_1_X_2[5][0],
                blanks_1[5][0],

                player_1_X_1[6][0],
                player_1_X_2[6][0],
                blanks_1[6][0],

                player_1_X_1[7][0],
                player_1_X_2[7][0],
                blanks_1[7][0],

                player_1_X_1[8][0],
                player_1_X_2[8][0],
                blanks_1[8][0],

                player_1_X_1[9][0],
                player_1_X_2[9][0],
                blanks_1[9][0],

                player_1_X_1[10][0],
                player_1_X_2[10][0],
                blanks_1[10][0],

                player_1_X_1[11][0],
                player_1_X_2[11][0],
                blanks_1[11][0],

                player_1_X_1[12][0],
                player_1_X_2[12][0],
                blanks_1[12][0],

                player_1_X_1[13][0],
                player_1_X_2[13][0],
                blanks_1[13][0],

                player_1_X_1[14][0],
                player_1_X_2[14][0],
                blanks_1[14][0],

                html.Div(children=team_names_json, id='intermediate-team_names_gw1', style={'display': 'none'}),
                html.Div(children=team_unique_ids_json, id='intermediate-team_unique_ids_gw1', style={'display': 'none'}),
                html.Div(children=players_2020_names_json, id='data2020-names-stored-json', style={'display': 'none'}),
                html.Div(children=players_2020_unique_ids_json, id='data2020-unique-ids-stored-json', style={'display': 'none'}),
                html.Div(children=str(round_curr), id='round_current', style={'display': 'none'}),
                html.Div(children=team_picks_json, id='team_data', style={'display': 'none'}),

            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+2'),

                html.Div([
                    html.Div(children='No.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Pos', id='pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Name', id='name', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Value (£)', id='Value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team', id='team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Agst.', id='Agst.', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Home/ Away', id='H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Player Form', id='player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team Form', id='team_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Odds (win)', id='team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Cpt.', id='captain', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Trn.', id='transfer', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),

                ], style={'width': '100%','float': 'left'}),

                player_2_X_1[0][0],
                player_2_X_2[0][0],
                blanks_2[0][0],

                player_2_X_1[1][0],
                player_2_X_2[1][0],
                blanks_2[1][0],

                player_2_X_1[2][0],
                player_2_X_2[2][0],
                blanks_2[2][0],

                player_2_X_1[3][0],
                player_2_X_2[3][0],
                blanks_2[3][0],

                player_2_X_1[4][0],
                player_2_X_2[4][0],
                blanks_2[4][0],

                player_2_X_1[5][0],
                player_2_X_2[5][0],
                blanks_2[5][0],

                player_2_X_1[6][0],
                player_2_X_2[6][0],
                blanks_2[6][0],

                player_2_X_1[7][0],
                player_2_X_2[7][0],
                blanks_2[7][0],

                player_2_X_1[8][0],
                player_2_X_2[8][0],
                blanks_2[8][0],

                player_2_X_1[9][0],
                player_2_X_2[9][0],
                blanks_2[9][0],

                player_2_X_1[10][0],
                player_2_X_2[10][0],
                blanks_2[10][0],

                player_2_X_1[11][0],
                player_2_X_2[11][0],
                blanks_2[11][0],

                player_2_X_1[12][0],
                player_2_X_2[12][0],
                blanks_2[12][0],

                player_2_X_1[13][0],
                player_2_X_2[13][0],
                blanks_2[13][0],

                player_2_X_1[14][0],
                player_2_X_2[14][0],
                blanks_2[14][0],

                html.Div(children=team_names_json, id='intermediate-team_names_gw2', style={'display': 'none'}),

                html.Div(children=team_unique_ids_json, id='intermediate-team_unique_ids_gw2', style={'display': 'none'}),

            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+3'),

                html.Div([
                    html.Div(children='No.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Pos', id='pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Name', id='name', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Value (£)', id='Value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team', id='team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Agst.', id='Agst.', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Home/ Away', id='H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Player Form', id='player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team Form', id='team_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Odds (win)', id='team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Cpt.', id='captain', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Trn.', id='transfer', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),

                ], style={'width': '100%','float': 'left'}),

                player_3_X_1[0][0],
                player_3_X_2[0][0],
                blanks_3[0][0],

                player_3_X_1[1][0],
                player_3_X_2[1][0],
                blanks_3[1][0],

                player_3_X_1[2][0],
                player_3_X_2[2][0],
                blanks_3[2][0],

                player_3_X_1[3][0],
                player_3_X_2[3][0],
                blanks_3[3][0],

                player_3_X_1[4][0],
                player_3_X_2[4][0],
                blanks_3[4][0],

                player_3_X_1[5][0],
                player_3_X_2[5][0],
                blanks_3[5][0],

                player_3_X_1[6][0],
                player_3_X_2[6][0],
                blanks_3[6][0],

                player_3_X_1[7][0],
                player_3_X_2[7][0],
                blanks_3[7][0],

                player_3_X_1[8][0],
                player_3_X_2[8][0],
                blanks_3[8][0],

                player_3_X_1[9][0],
                player_3_X_2[9][0],
                blanks_3[9][0],

                player_3_X_1[10][0],
                player_3_X_2[10][0],
                blanks_3[10][0],

                player_3_X_1[11][0],
                player_3_X_2[11][0],
                blanks_3[11][0],

                player_3_X_1[12][0],
                player_3_X_2[12][0],
                blanks_3[12][0],

                player_3_X_1[13][0],
                player_3_X_2[13][0],
                blanks_3[13][0],

                player_3_X_1[14][0],
                player_3_X_2[14][0],
                blanks_3[14][0],

                html.Div(children=team_names_json, id='intermediate-team_names_gw3', style={'display': 'none'}),
                html.Div(children=team_unique_ids_json, id='intermediate-team_unique_ids_gw3', style={'display': 'none'}),

            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+4'),

                html.Div([
                    html.Div(children='No.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Pos', id='pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Name', id='name', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Value (£)', id='Value', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team', id='team', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Agst.', id='Agst.', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Home/ Away', id='H_A', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Player Form', id='player_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team Form', id='team_form', style={'width': '7%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Odds (win)', id='team_odds', style={'width': '5%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Cpt.', id='captain', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Trn.', id='transfer', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),

                ], style={'width': '100%','float': 'left'}),

                player_4_X_1[0][0],
                player_4_X_2[0][0],
                blanks_4[0][0],

                player_4_X_1[1][0],
                player_4_X_2[1][0],
                blanks_4[1][0],

                player_4_X_1[2][0],
                player_4_X_2[2][0],
                blanks_4[2][0],

                player_4_X_1[3][0],
                player_4_X_2[3][0],
                blanks_4[3][0],

                player_4_X_1[4][0],
                player_4_X_2[4][0],
                blanks_4[4][0],

                player_4_X_1[5][0],
                player_4_X_2[5][0],
                blanks_4[5][0],

                player_4_X_1[6][0],
                player_4_X_2[6][0],
                blanks_4[6][0],

                player_4_X_1[7][0],
                player_4_X_2[7][0],
                blanks_4[7][0],

                player_4_X_1[8][0],
                player_4_X_2[8][0],
                blanks_4[8][0],

                player_4_X_1[9][0],
                player_4_X_2[9][0],
                blanks_4[9][0],

                player_4_X_1[10][0],
                player_4_X_2[10][0],
                blanks_4[10][0],

                player_4_X_1[11][0],
                player_4_X_2[11][0],
                blanks_4[11][0],

                player_4_X_1[12][0],
                player_4_X_2[12][0],
                blanks_4[12][0],

                player_4_X_1[13][0],
                player_4_X_2[13][0],
                blanks_4[13][0],

                player_4_X_1[14][0],
                player_4_X_2[14][0],
                blanks_4[14][0],

                html.Div(children=team_names_json, id='intermediate-team_names_gw4', style={'display': 'none'}),

                html.Div(children=team_unique_ids_json, id='intermediate-team_unique_ids_gw4', style={'display': 'none'}),

            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),
            )


@app.callback(
    [Output('player_1_1_1_value', 'children'),
     Output('player_1_1_1_pos', 'children'),
     Output('player_1_1_1_team', 'children'),
     Output('player_1_1_1_against', 'children'),
     Output('player_1_1_1_H_A', 'children'),
     Output('player_1_1_1_team_odds', 'children'),
     Output('player_1_1_1_player_form', 'children'),
     Output('player_1_1_2_against', 'children'),
     Output('player_1_1_2_H_A', 'children'),
     Output('player_1_1_2_team_odds', 'children'),
     Output('player_1_1_2_player_form', 'children'),
     Output('player_2_1_name', 'options'),
     Output('player_2_1_name', 'value'),
     Output('intermediate-team_names_gw1', 'children'),
     Output('intermediate-team_unique_ids_gw1', 'children'),
     Output('intermediate-team_names_gw2', 'children'),
     Output('intermediate-team_unique_ids_gw2', 'children'),
     Output('player_3_1_1_against', 'style'),
     Output('player_3_1_2_against', 'style')],
    [Input('player_1_1_name', 'value')],
    [State('intermediate-team_names_gw1', 'children'),
     State('intermediate-team_unique_ids_gw1', 'children'),
     State('intermediate-team_names_gw2', 'children'),
     State('intermediate-team_unique_ids_gw2', 'children'),
     State('round_current', 'children'),
     State('team_data', 'children')]
)
def update_player_data_gw1_p1(player_unique_id,
                                team_names_json,
                                team_unique_ids_json,
                                team_names_json_next,
                                team_unique_ids_json_next,
                                gw_curr,
                                team_picks_json):


    team_picks = pd.read_json(team_picks_json, orient='split', typ='frame')

    data_2020 = data[data['season']==2020]

    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')
    team_names = pd.read_json(team_names_json, orient='split', typ='series')

    team_unique_ids_next = pd.read_json(team_unique_ids_json_next, orient='split', typ='series')
    team_names_next = pd.read_json(team_names_json_next, orient='split', typ='series')

    gw_curr = int(gw_curr)
    gw_next = gw_curr + 1

    #GW + 1
    player_id = determine_element_id(data, player_unique_id, 2020)
    (unique_id, form, team_unique_id, team_id, position, team_code, player_name, opposition, was_home, odds_win, fixture_diff, n_matches) = \
            planner_process_player(data, team_codes, fixture_data, player_id, season_latest, gw_next)

    if int(unique_id) in team_unique_ids.values:
        value = '{0:.1f}'.format(team_picks[team_picks['element']==player_id]['selling_price'].values[0]/10)
    else:
        round_player_max = data_2020[(data_2020['unique_id']==unique_id)]['round'].max()
        value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)

    #GW next + 1
    unique_id_next = unique_id
    if unique_id_next not in team_unique_ids.unique():
        team_names_next.iloc[0] = player_name
        team_unique_ids_next.iloc[0] = unique_id

    player_options_next = [{'label': name, 'value': team_unique_ids_next[i]} for i, name in enumerate(team_names_next)]

    team_names_json_next = team_names_next.to_json(date_format='iso', orient='split')
    team_unique_ids_json_next = team_unique_ids_next.to_json(date_format='iso', orient='split')


    return (value,
            position,
            team_code,
            opposition[0],
            was_home[0],
            odds_win[0],
            form[0],
            opposition[1],
            was_home[1],
            odds_win[1],
            form[1],
            player_options_next,
            unique_id_next,
            team_names_json, team_unique_ids_json, team_names_json_next, team_unique_ids_json_next,
            player_opposition_style(font_size, fixture_diff[0]),
            player_opposition_style(font_size, fixture_diff[1]))


@app.callback(
    [Output('player_2_1_1_value', 'children'),
     Output('player_2_1_1_pos', 'children'),
     Output('player_2_1_1_team', 'children'),
     Output('player_2_1_1_against', 'children'),
     Output('player_2_1_1_H_A', 'children'),
     Output('player_2_1_1_team_odds', 'children'),
     Output('player_2_1_1_player_form', 'children'),
     Output('player_2_1_2_against', 'children'),
     Output('player_2_1_2_H_A', 'children'),
     Output('player_2_1_2_team_odds', 'children'),
     Output('player_2_1_2_player_form', 'children'),
     Output('player_3_1_name', 'options'),
     Output('player_3_1_name', 'value'),
     Output('intermediate-team_names_gw2', 'children'),
     Output('intermediate-team_unique_ids_gw2', 'children'),
     Output('intermediate-team_names_gw3', 'children'),
     Output('intermediate-team_unique_ids_gw3', 'children'),
     Output('player_3_1_1_against', 'style'),
     Output('player_3_1_2_against', 'style')],
    [Input('player_2_1_name', 'value')],
    [State('intermediate-team_names_gw2', 'children'),
     State('intermediate-team_unique_ids_gw2', 'children'),
     State('intermediate-team_names_gw3', 'children'),
     State('intermediate-team_unique_ids_gw3', 'children'),
     State('round_current', 'children'),
     State('team_data', 'children')]
)
def update_player_data_gw2_p1(player_unique_id,
                                team_names_json,
                                team_unique_ids_json,
                                team_names_json_next,
                                team_unique_ids_json_next,
                                gw_curr,
                                team_picks_json):

    team_picks = pd.read_json(team_picks_json, orient='split', typ='frame')

    data_2020 = data[data['season']==2020]

    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')
    team_names = pd.read_json(team_names_json, orient='split', typ='series')

    team_unique_ids_next = pd.read_json(team_unique_ids_json_next, orient='split', typ='series')
    team_names_next = pd.read_json(team_names_json_next, orient='split', typ='series')

    gw_curr = int(gw_curr)
    gw_next = gw_curr + 2

    #GW next
    player_id = determine_element_id(data, player_unique_id, 2020)
    (unique_id, form, team_unique_id, team_id, position, team_code, player_name, opposition, was_home, odds_win, fixture_diff, n_matches) = \
            planner_process_player(data, team_codes, fixture_data, player_id, season_latest, gw_next)

    if int(unique_id) in team_unique_ids.values:
        value = '{0:.1f}'.format(team_picks[team_picks['element']==player_id]['selling_price'].values[0]/10)
    else:
        round_player_max = data_2020[(data_2020['unique_id']==unique_id)]['round'].max()
        value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)

    #GW next + 1
    unique_id_next = unique_id
    if unique_id_next not in team_unique_ids.unique():
        team_names_next.iloc[0] = player_name
        team_unique_ids_next.iloc[0] = unique_id

    player_options_next = [{'label': name, 'value': team_unique_ids_next[i]} for i, name in enumerate(team_names_next)]

    team_names_json_next = team_names_next.to_json(date_format='iso', orient='split')
    team_unique_ids_json_next = team_unique_ids_next.to_json(date_format='iso', orient='split')


    return (value,
            position,
            team_code,
            opposition[0],
            was_home[0],
            odds_win[0],
            form[0],
            opposition[1],
            was_home[1],
            odds_win[1],
            form[1],
            player_options_next,
            unique_id_next,
            team_names_json, team_unique_ids_json, team_names_json_next, team_unique_ids_json_next,
            player_opposition_style(font_size, fixture_diff[0]),
            player_opposition_style(font_size, fixture_diff[1]))


@app.callback(
    [Output('player_3_1_1_value', 'children'),
     Output('player_3_1_1_pos', 'children'),
     Output('player_3_1_1_team', 'children'),
     Output('player_3_1_1_against', 'children'),
     Output('player_3_1_1_H_A', 'children'),
     Output('player_3_1_1_team_odds', 'children'),
     Output('player_3_1_1_player_form', 'children'),
     Output('player_3_1_2_against', 'children'),
     Output('player_3_1_2_H_A', 'children'),
     Output('player_3_1_2_team_odds', 'children'),
     Output('player_3_1_2_player_form', 'children'),
     Output('player_4_1_name', 'options'),
     Output('player_4_1_name', 'value'),
     Output('intermediate-team_names_gw3', 'children'),
     Output('intermediate-team_unique_ids_gw3', 'children'),
     Output('intermediate-team_names_gw4', 'children'),
     Output('intermediate-team_unique_ids_gw4', 'children'),
     Output('player_3_1_1_against', 'style'),
     Output('player_3_1_2_against', 'style')],
    [Input('player_3_1_name', 'value')],
    [State('intermediate-team_names_gw3', 'children'),
     State('intermediate-team_unique_ids_gw3', 'children'),
     State('intermediate-team_names_gw4', 'children'),
     State('intermediate-team_unique_ids_gw4', 'children'),
     State('round_current', 'children'),
     State('team_data', 'children')]
)
def update_player_data_gw3_p1(player_unique_id,
                                team_names_json,
                                team_unique_ids_json,
                                team_names_json_next,
                                team_unique_ids_json_next,
                                gw_curr,
                                team_picks_json):

    team_picks = pd.read_json(team_picks_json, orient='split', typ='frame')

    data_2020 = data[data['season']==2020]

    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')
    team_names = pd.read_json(team_names_json, orient='split', typ='series')

    team_unique_ids_next = pd.read_json(team_unique_ids_json_next, orient='split', typ='series')
    team_names_next = pd.read_json(team_names_json_next, orient='split', typ='series')

    gw_curr = int(gw_curr)
    gw_next = gw_curr + 3

    #GW next
    player_id = determine_element_id(data, player_unique_id, 2020)
    (unique_id, form, team_unique_id, team_id, position, team_code, player_name, opposition, was_home, odds_win, fixture_diff, n_matches) = \
            planner_process_player(data, team_codes, fixture_data, player_id, season_latest, gw_next)

    if int(unique_id) in team_unique_ids.values:
        value = '{0:.1f}'.format(team_picks[team_picks['element']==player_id]['selling_price'].values[0]/10)
    else:
        round_player_max = data_2020[(data_2020['unique_id']==unique_id)]['round'].max()
        value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)

    #GW next + 1
    unique_id_next = unique_id
    if unique_id_next not in team_unique_ids.unique():
        team_names_next.iloc[0] = player_name
        team_unique_ids_next.iloc[0] = unique_id

    player_options_next = [{'label': name, 'value': team_unique_ids_next[i]} for i, name in enumerate(team_names_next)]

    team_names_json_next = team_names_next.to_json(date_format='iso', orient='split')
    team_unique_ids_json_next = team_unique_ids_next.to_json(date_format='iso', orient='split')

    return (value,
            position,
            team_code,
            opposition[0],
            was_home[0],
            odds_win[0],
            form[0],
            opposition[1],
            was_home[1],
            odds_win[1],
            form[1],
            player_options_next,
            unique_id_next,
            team_names_json, team_unique_ids_json, team_names_json_next, team_unique_ids_json_next,
            player_opposition_style(font_size, fixture_diff[0]),
            player_opposition_style(font_size, fixture_diff[1]))


@app.callback(
    [Output('player_4_1_1_value', 'children'),
     Output('player_4_1_1_pos', 'children'),
     Output('player_4_1_1_team', 'children'),
     Output('player_4_1_1_against', 'children'),
     Output('player_4_1_1_H_A', 'children'),
     Output('player_4_1_1_team_odds', 'children'),
     Output('player_4_1_1_player_form', 'children'),
     Output('player_4_1_2_against', 'children'),
     Output('player_4_1_2_H_A', 'children'),
     Output('player_4_1_2_team_odds', 'children'),
     Output('player_4_1_2_player_form', 'children'),
     Output('intermediate-team_names_gw4', 'children'),
     Output('intermediate-team_unique_ids_gw4', 'children'),
     Output('player_3_1_1_against', 'style'),
     Output('player_3_1_2_against', 'style')],
    [Input('player_4_1_name', 'value')],
    [State('intermediate-team_names_gw4', 'children'),
     State('intermediate-team_unique_ids_gw4', 'children'),
     State('round_current', 'children'),
     State('team_data', 'children')]
)
def update_player_data_gw4_p1(player_unique_id,
                                team_names_json,
                                team_unique_ids_json,
                                gw_curr,
                                team_picks_json):

    team_picks = pd.read_json(team_picks_json, orient='split', typ='frame')

    data_2020 = data[data['season']==2020]

    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')
    team_names = pd.read_json(team_names_json, orient='split', typ='series')

    gw_curr = int(gw_curr)
    gw_next = gw_curr + 4

    #GW next
    player_id = determine_element_id(data, player_unique_id, 2020)
    (unique_id, form, team_unique_id, team_id, position, team_code, player_name, opposition, was_home, odds_win, fixture_diff, n_matches) = \
            planner_process_player(data, team_codes, fixture_data, player_id, season_latest, gw_next)

    if int(unique_id) in team_unique_ids.values:
        value = '{0:.1f}'.format(team_picks[team_picks['element']==player_id]['selling_price'].values[0]/10)
    else:
        round_player_max = data_2020[(data_2020['unique_id']==unique_id)]['round'].max()
        value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)


    return (value,
            position,
            team_code,
            opposition[0],
            was_home[0],
            odds_win[0],
            form[0],
            opposition[1],
            was_home[1],
            odds_win[1],
            form[1],
            team_names_json, team_unique_ids_json,
            player_opposition_style(font_size, fixture_diff[0]),
            player_opposition_style(font_size, fixture_diff[1]))


# @app.callback(
#     [Output('player_1_1_1_value', 'children'),
#      Output('player_1_1_1_pos', 'children'),
#      Output('player_1_1_1_team', 'children'),
#      Output('player_1_1_1_against', 'children'),
#      Output('player_1_1_1_H_A', 'children'),
#      Output('player_1_1_1_team_odds', 'children'),
#      Output('player_1_1_1_player_form', 'children'),
#      Output('player_1_1_2_against', 'children'),
#      Output('player_1_1_2_H_A', 'children'),
#      Output('player_1_1_2_team_odds', 'children'),
#      Output('player_1_1_2_player_form', 'children'),
#      Output('player_1_2_1_value', 'children'),
#      Output('player_1_2_1_pos', 'children'),
#      Output('player_1_2_1_team', 'children'),
#      Output('player_1_2_1_against', 'children'),
#      Output('player_1_2_1_H_A', 'children'),
#      Output('player_1_2_1_team_odds', 'children'),
#      Output('player_1_2_1_player_form', 'children'),
#      Output('player_1_2_2_against', 'children'),
#      Output('player_1_2_2_H_A', 'children'),
#      Output('player_1_2_2_team_odds', 'children'),
#      Output('player_1_2_2_player_form', 'children'),
#      Output('player_1_3_1_value', 'children'),
#      Output('player_1_3_1_pos', 'children'),
#      Output('player_1_3_1_team', 'children'),
#      Output('player_1_3_1_against', 'children'),
#      Output('player_1_3_1_H_A', 'children'),
#      Output('player_1_3_1_team_odds', 'children'),
#      Output('player_1_3_1_player_form', 'children'),
#      Output('player_1_3_2_against', 'children'),
#      Output('player_1_3_2_H_A', 'children'),
#      Output('player_1_3_2_team_odds', 'children'),
#      Output('player_1_3_2_player_form', 'children'),
#      Output('player_1_4_1_value', 'children'),
#      Output('player_1_4_1_pos', 'children'),
#      Output('player_1_4_1_team', 'children'),
#      Output('player_1_4_1_against', 'children'),
#      Output('player_1_4_1_H_A', 'children'),
#      Output('player_1_4_1_team_odds', 'children'),
#      Output('player_1_4_1_player_form', 'children'),
#      Output('player_1_4_2_against', 'children'),
#      Output('player_1_4_2_H_A', 'children'),
#      Output('player_1_4_2_team_odds', 'children'),
#      Output('player_1_4_2_player_form', 'children'),
#      Output('player_1_5_1_value', 'children'),
#      Output('player_1_5_1_pos', 'children'),
#      Output('player_1_5_1_team', 'children'),
#      Output('player_1_5_1_against', 'children'),
#      Output('player_1_5_1_H_A', 'children'),
#      Output('player_1_5_1_team_odds', 'children'),
#      Output('player_1_5_1_player_form', 'children'),
#      Output('player_1_5_2_against', 'children'),
#      Output('player_1_5_2_H_A', 'children'),
#      Output('player_1_5_2_team_odds', 'children'),
#      Output('player_1_5_2_player_form', 'children'),
#      Output('player_1_6_1_value', 'children'),
#      Output('player_1_6_1_pos', 'children'),
#      Output('player_1_6_1_team', 'children'),
#      Output('player_1_6_1_against', 'children'),
#      Output('player_1_6_1_H_A', 'children'),
#      Output('player_1_6_1_team_odds', 'children'),
#      Output('player_1_6_1_player_form', 'children'),
#      Output('player_1_6_2_against', 'children'),
#      Output('player_1_6_2_H_A', 'children'),
#      Output('player_1_6_2_team_odds', 'children'),
#      Output('player_1_6_2_player_form', 'children'),
#      Output('player_1_7_1_value', 'children'),
#      Output('player_1_7_1_pos', 'children'),
#      Output('player_1_7_1_team', 'children'),
#      Output('player_1_7_1_against', 'children'),
#      Output('player_1_7_1_H_A', 'children'),
#      Output('player_1_7_1_team_odds', 'children'),
#      Output('player_1_7_1_player_form', 'children'),
#      Output('player_1_7_2_against', 'children'),
#      Output('player_1_7_2_H_A', 'children'),
#      Output('player_1_7_2_team_odds', 'children'),
#      Output('player_1_7_2_player_form', 'children'),
#      Output('player_1_8_1_value', 'children'),
#      Output('player_1_8_1_pos', 'children'),
#      Output('player_1_8_1_team', 'children'),
#      Output('player_1_8_1_against', 'children'),
#      Output('player_1_8_1_H_A', 'children'),
#      Output('player_1_8_1_team_odds', 'children'),
#      Output('player_1_8_1_player_form', 'children'),
#      Output('player_1_8_2_against', 'children'),
#      Output('player_1_8_2_H_A', 'children'),
#      Output('player_1_8_2_team_odds', 'children'),
#      Output('player_1_8_2_player_form', 'children'),
#      Output('player_1_9_1_value', 'children'),
#      Output('player_1_9_1_pos', 'children'),
#      Output('player_1_9_1_team', 'children'),
#      Output('player_1_9_1_against', 'children'),
#      Output('player_1_9_1_H_A', 'children'),
#      Output('player_1_9_1_team_odds', 'children'),
#      Output('player_1_9_1_player_form', 'children'),
#      Output('player_1_9_2_against', 'children'),
#      Output('player_1_9_2_H_A', 'children'),
#      Output('player_1_9_2_team_odds', 'children'),
#      Output('player_1_9_2_player_form', 'children'),
#      Output('player_1_10_1_value', 'children'),
#      Output('player_1_10_1_pos', 'children'),
#      Output('player_1_10_1_team', 'children'),
#      Output('player_1_10_1_against', 'children'),
#      Output('player_1_10_1_H_A', 'children'),
#      Output('player_1_10_1_team_odds', 'children'),
#      Output('player_1_10_1_player_form', 'children'),
#      Output('player_1_10_2_against', 'children'),
#      Output('player_1_10_2_H_A', 'children'),
#      Output('player_1_10_2_team_odds', 'children'),
#      Output('player_1_10_2_player_form', 'children'),
#      Output('player_1_11_1_value', 'children'),
#      Output('player_1_11_1_pos', 'children'),
#      Output('player_1_11_1_team', 'children'),
#      Output('player_1_11_1_against', 'children'),
#      Output('player_1_11_1_H_A', 'children'),
#      Output('player_1_11_1_team_odds', 'children'),
#      Output('player_1_11_1_player_form', 'children'),
#      Output('player_1_11_2_against', 'children'),
#      Output('player_1_11_2_H_A', 'children'),
#      Output('player_1_11_2_team_odds', 'children'),
#      Output('player_1_11_2_player_form', 'children'),
#      Output('player_1_12_1_value', 'children'),
#      Output('player_1_12_1_pos', 'children'),
#      Output('player_1_12_1_team', 'children'),
#      Output('player_1_12_1_against', 'children'),
#      Output('player_1_12_1_H_A', 'children'),
#      Output('player_1_12_1_team_odds', 'children'),
#      Output('player_1_12_1_player_form', 'children'),
#      Output('player_1_12_2_against', 'children'),
#      Output('player_1_12_2_H_A', 'children'),
#      Output('player_1_12_2_team_odds', 'children'),
#      Output('player_1_12_2_player_form', 'children'),
#      Output('player_1_13_1_value', 'children'),
#      Output('player_1_13_1_pos', 'children'),
#      Output('player_1_13_1_team', 'children'),
#      Output('player_1_13_1_against', 'children'),
#      Output('player_1_13_1_H_A', 'children'),
#      Output('player_1_13_1_team_odds', 'children'),
#      Output('player_1_13_1_player_form', 'children'),
#      Output('player_1_13_2_against', 'children'),
#      Output('player_1_13_2_H_A', 'children'),
#      Output('player_1_13_2_team_odds', 'children'),
#      Output('player_1_13_2_player_form', 'children'),
#      Output('player_1_14_1_value', 'children'),
#      Output('player_1_14_1_pos', 'children'),
#      Output('player_1_14_1_team', 'children'),
#      Output('player_1_14_1_against', 'children'),
#      Output('player_1_14_1_H_A', 'children'),
#      Output('player_1_14_1_team_odds', 'children'),
#      Output('player_1_14_1_player_form', 'children'),
#      Output('player_1_14_2_against', 'children'),
#      Output('player_1_14_2_H_A', 'children'),
#      Output('player_1_14_2_team_odds', 'children'),
#      Output('player_1_14_2_player_form', 'children'),
#      Output('player_1_15_1_value', 'children'),
#      Output('player_1_15_1_pos', 'children'),
#      Output('player_1_15_1_team', 'children'),
#      Output('player_1_15_1_against', 'children'),
#      Output('player_1_15_1_H_A', 'children'),
#      Output('player_1_15_1_team_odds', 'children'),
#      Output('player_1_15_1_player_form', 'children'),
#      Output('player_1_15_2_against', 'children'),
#      Output('player_1_15_2_H_A', 'children'),
#      Output('player_1_15_2_team_odds', 'children'),
#      Output('player_1_15_2_player_form', 'children'),
#      Output('player_2_1_name', 'options'),
#      Output('player_2_1_name', 'value'),
#      Output('player_2_2_name', 'options'),
#      Output('player_2_2_name', 'value'),
#      Output('player_2_3_name', 'options'),
#      Output('player_2_3_name', 'value'),
#      Output('player_2_4_name', 'options'),
#      Output('player_2_4_name', 'value'),
#      Output('player_2_5_name', 'options'),
#      Output('player_2_5_name', 'value'),
#      Output('player_2_6_name', 'options'),
#      Output('player_2_6_name', 'value'),
#      Output('player_2_7_name', 'options'),
#      Output('player_2_7_name', 'value'),
#      Output('player_2_8_name', 'options'),
#      Output('player_2_8_name', 'value'),
#      Output('player_2_9_name', 'options'),
#      Output('player_2_9_name', 'value'),
#      Output('player_2_10_name', 'options'),
#      Output('player_2_10_name', 'value'),
#      Output('player_2_11_name', 'options'),
#      Output('player_2_11_name', 'value'),
#      Output('player_2_12_name', 'options'),
#      Output('player_2_12_name', 'value'),
#      Output('player_2_13_name', 'options'),
#      Output('player_2_13_name', 'value'),
#      Output('player_2_14_name', 'options'),
#      Output('player_2_14_name', 'value'),
#      Output('player_2_15_name', 'options'),
#      Output('player_2_15_name', 'value'),
#      Output('intermediate-team_names_gw1', 'children'),
#      Output('intermediate-team_unique_ids_gw1', 'children'),
#      Output('intermediate-team_names_gw2', 'children'),
#      Output('intermediate-team_unique_ids_gw2', 'children')],
#     [Input('player_1_1_name', 'value'),
#      Input('player_1_2_name', 'value'),
#      Input('player_1_3_name', 'value'),
#      Input('player_1_4_name', 'value'),
#      Input('player_1_5_name', 'value'),
#      Input('player_1_6_name', 'value'),
#      Input('player_1_7_name', 'value'),
#      Input('player_1_8_name', 'value'),
#      Input('player_1_9_name', 'value'),
#      Input('player_1_10_name', 'value'),
#      Input('player_1_11_name', 'value'),
#      Input('player_1_12_name', 'value'),
#      Input('player_1_13_name', 'value'),
#      Input('player_1_14_name', 'value'),
#      Input('player_1_15_name', 'value')],
#     [State('intermediate-team_names_gw1', 'children'),
#      State('intermediate-team_unique_ids_gw1', 'children'),
#      State('intermediate-team_names_gw2', 'children'),
#      State('intermediate-team_unique_ids_gw2', 'children')]
# )
# def update_player_data_gw1(player_1_1_unique_id,
#                             player_1_2_unique_id,
#                             player_1_3_unique_id,
#                             player_1_4_unique_id,
#                             player_1_5_unique_id,
#                             player_1_6_unique_id,
#                             player_1_7_unique_id,
#                             player_1_8_unique_id,
#                             player_1_9_unique_id,
#                             player_1_10_unique_id,
#                             player_1_11_unique_id,
#                             player_1_12_unique_id,
#                             player_1_13_unique_id,
#                             player_1_14_unique_id,
#                             player_1_15_unique_id,
#                             team_names_json_1,
#                             team_unique_ids_json_1,
#                             team_names_json_2,
#                             team_unique_ids_json_2):
#
#     email = 'speeder1987@gmail.com'
#     password = 'Footb@ll2020'
#     team_id = '5403039'
#     team_picks = DataLoaderObj.scrape_team_information(email, password, team_id)
#
#     data_2020 = data[data['season']==2020]
#
#     team_unique_ids_1 = pd.read_json(team_unique_ids_json_1, orient='split', typ='series')
#     team_names_1 = pd.read_json(team_names_json_1, orient='split', typ='series')
#
#     team_unique_ids_2 = pd.read_json(team_unique_ids_json_2, orient='split', typ='series')
#     team_names_2 = pd.read_json(team_names_json_2, orient='split', typ='series')
#
#     gw_curr = 17
#
#     gw_plus1 = gw_curr + 1
#     gw_plus2 = gw_curr + 2
#     gw_plus3 = gw_curr + 3
#     gw_plus4 = gw_curr + 4
#
#     #GW + 1
#     player_1_1_id = determine_element_id(data, player_1_1_unique_id, 2020)
#     (player_1_1_unique_id, player_1_1_player_form, player_1_1_team_unique_id, player_1_1_team_id, player_1_1_position, player_1_1_team_code, player_1_1_player_name, player_1_1_opposition, player_1_1_was_home, player_1_1_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_1_id, season_latest, gw_plus1)
#
#     if int(player_1_1_unique_id) in team_unique_ids_1.values:
#         player_1_1_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_1_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_1_unique_id)]['round'].max()
#         player_1_1_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_1_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 2
#     player_1_2_id = determine_element_id(data, player_1_2_unique_id, 2020)
#     (player_1_2_unique_id, player_1_2_player_form, player_1_2_team_unique_id, player_1_2_team_id, player_1_2_position, player_1_2_team_code, player_1_2_player_name, player_1_2_opposition, player_1_2_was_home, player_1_2_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_2_id, season_latest, gw_plus1)
#
#     if int(player_1_2_unique_id) in team_unique_ids_1.values:
#         player_1_2_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_2_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_2_unique_id)]['round'].max()
#         player_1_2_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_2_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 3
#     player_1_3_id = determine_element_id(data, player_1_3_unique_id, 2020)
#     (player_1_3_unique_id, player_1_3_player_form, player_1_3_team_unique_id, player_1_3_team_id, player_1_3_position, player_1_3_team_code, player_1_3_player_name, player_1_3_opposition, player_1_3_was_home, player_1_3_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_3_id, season_latest, gw_plus1)
#
#     if int(player_1_3_unique_id) in team_unique_ids_1.values:
#         player_1_3_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_3_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_3_unique_id)]['round'].max()
#         player_1_3_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_3_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 4
#     player_1_4_id = determine_element_id(data, player_1_4_unique_id, 2020)
#     (player_1_4_unique_id, player_1_4_player_form, player_1_4_team_unique_id, player_1_4_team_id, player_1_4_position, player_1_4_team_code, player_1_4_player_name, player_1_4_opposition, player_1_4_was_home, player_1_4_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_4_id, season_latest, gw_plus1)
#
#     if int(player_1_4_unique_id) in team_unique_ids_1.values:
#         player_1_4_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_4_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_4_unique_id)]['round'].max()
#         player_1_4_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_4_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 5
#     player_1_5_id = determine_element_id(data, player_1_5_unique_id, 2020)
#     (player_1_5_unique_id, player_1_5_player_form, player_1_5_team_unique_id, player_1_5_team_id, player_1_5_position, player_1_5_team_code, player_1_5_player_name, player_1_5_opposition, player_1_5_was_home, player_1_5_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_5_id, season_latest, gw_plus1)
#
#     if int(player_1_5_unique_id) in team_unique_ids_1.values:
#         player_1_5_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_5_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_5_unique_id)]['round'].max()
#         player_1_5_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_5_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 6
#     player_1_6_id = determine_element_id(data, player_1_6_unique_id, 2020)
#     (player_1_6_unique_id, player_1_6_player_form, player_1_6_team_unique_id, player_1_6_team_id, player_1_6_position, player_1_6_team_code, player_1_6_player_name, player_1_6_opposition, player_1_6_was_home, player_1_6_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_6_id, season_latest, gw_plus1)
#
#     if int(player_1_6_unique_id) in team_unique_ids_1.values:
#         player_1_6_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_6_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_6_unique_id)]['round'].max()
#         player_1_6_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_6_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 7
#     player_1_7_id = determine_element_id(data, player_1_7_unique_id, 2020)
#     (player_1_7_unique_id, player_1_7_player_form, player_1_7_team_unique_id, player_1_7_team_id, player_1_7_position, player_1_7_team_code, player_1_7_player_name, player_1_7_opposition, player_1_7_was_home, player_1_7_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_7_id, season_latest, gw_plus1)
#
#     if int(player_1_7_unique_id) in team_unique_ids_1.values:
#         player_1_7_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_7_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_7_unique_id)]['round'].max()
#         player_1_7_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_7_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 8
#     player_1_8_id = determine_element_id(data, player_1_8_unique_id, 2020)
#     (player_1_8_unique_id, player_1_8_player_form, player_1_8_team_unique_id, player_1_8_team_id, player_1_8_position, player_1_8_team_code, player_1_8_player_name, player_1_8_opposition, player_1_8_was_home, player_1_8_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_8_id, season_latest, gw_plus1)
#
#     if int(player_1_8_unique_id) in team_unique_ids_1.values:
#         player_1_8_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_8_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_8_unique_id)]['round'].max()
#         player_1_8_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_8_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 9
#     player_1_9_id = determine_element_id(data, player_1_9_unique_id, 2020)
#     (player_1_9_unique_id, player_1_9_player_form, player_1_9_team_unique_id, player_1_9_team_id, player_1_9_position, player_1_9_team_code, player_1_9_player_name, player_1_9_opposition, player_1_9_was_home, player_1_9_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_9_id, season_latest, gw_plus1)
#
#     if int(player_1_9_unique_id) in team_unique_ids_1.values:
#         player_1_9_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_9_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_9_unique_id)]['round'].max()
#         player_1_9_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_9_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 10
#     player_1_10_id = determine_element_id(data, player_1_10_unique_id, 2020)
#     (player_1_10_unique_id, player_1_10_player_form, player_1_10_team_unique_id, player_1_10_team_id, player_1_10_position, player_1_10_team_code, player_1_10_player_name, player_1_10_opposition, player_1_10_was_home, player_1_10_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_10_id, season_latest, gw_plus1)
#
#     if int(player_1_10_unique_id) in team_unique_ids_1.values:
#         player_1_10_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_10_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_10_unique_id)]['round'].max()
#         player_1_10_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_10_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 11
#     player_1_11_id = determine_element_id(data, player_1_11_unique_id, 2020)
#     (player_1_11_unique_id, player_1_11_player_form, player_1_11_team_unique_id, player_1_11_team_id, player_1_11_position, player_1_11_team_code, player_1_11_player_name, player_1_11_opposition, player_1_11_was_home, player_1_11_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_11_id, season_latest, gw_plus1)
#
#     if int(player_1_11_unique_id) in team_unique_ids_1.values:
#         player_1_11_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_11_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_11_unique_id)]['round'].max()
#         player_1_11_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_11_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 12
#     player_1_12_id = determine_element_id(data, player_1_12_unique_id, 2020)
#     (player_1_12_unique_id, player_1_12_player_form, player_1_12_team_unique_id, player_1_12_team_id, player_1_12_position, player_1_12_team_code, player_1_12_player_name, player_1_12_opposition, player_1_12_was_home, player_1_12_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_12_id, season_latest, gw_plus1)
#
#     if int(player_1_12_unique_id) in team_unique_ids_1.values:
#         player_1_12_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_12_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_12_unique_id)]['round'].max()
#         player_1_12_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_12_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 13
#     player_1_13_id = determine_element_id(data, player_1_13_unique_id, 2020)
#     (player_1_13_unique_id, player_1_13_player_form, player_1_13_team_unique_id, player_1_13_team_id, player_1_13_position, player_1_13_team_code, player_1_13_player_name, player_1_13_opposition, player_1_13_was_home, player_1_13_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_13_id, season_latest, gw_plus1)
#
#     if int(player_1_13_unique_id) in team_unique_ids_1.values:
#         player_1_13_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_13_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_13_unique_id)]['round'].max()
#         player_1_13_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_13_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 14
#     player_1_14_id = determine_element_id(data, player_1_14_unique_id, 2020)
#     (player_1_14_unique_id, player_1_14_player_form, player_1_14_team_unique_id, player_1_14_team_id, player_1_14_position, player_1_14_team_code, player_1_14_player_name, player_1_14_opposition, player_1_14_was_home, player_1_14_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_14_id, season_latest, gw_plus1)
#
#     if int(player_1_14_unique_id) in team_unique_ids_1.values:
#         player_1_14_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_14_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_14_unique_id)]['round'].max()
#         player_1_14_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_14_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#     # Player 15
#     player_1_15_id = determine_element_id(data, player_1_15_unique_id, 2020)
#     (player_1_15_unique_id, player_1_15_player_form, player_1_15_team_unique_id, player_1_15_team_id, player_1_15_position, player_1_15_team_code, player_1_15_player_name, player_1_15_opposition, player_1_15_was_home, player_1_15_odds_win, n_matches) = \
#             planner_process_player(data, team_codes, fixture_data, player_1_15_id, season_latest, gw_plus1)
#
#     if int(player_1_15_unique_id) in team_unique_ids_1.values:
#         player_1_15_value = '{0:.1f}'.format(team_picks[team_picks['element']==player_1_15_id]['selling_price'].values[0]/10)
#     else:
#         round_player_max = data_2020[(data_2020['unique_id']==player_1_15_unique_id)]['round'].max()
#         player_1_15_value = '{0:.1f}'.format(data_2020[(data_2020['unique_id']==player_1_15_unique_id) & (data_2020['round']==round_player_max)]['value'].values[0]/10)
#
#
#
#     #GW + 2
#
#     #Player 1
#     player_2_1_value = player_1_1_unique_id
#     if player_2_1_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_1_player_name
#         team_unique_ids_2.iloc[0] = player_1_1_unique_id
#
#     player_2_1_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 2
#     player_2_2_value = player_1_2_unique_id
#     if player_2_2_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_2_player_name
#         team_unique_ids_2.iloc[0] = player_1_2_unique_id
#
#     player_2_2_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 3
#     player_2_3_value = player_1_3_unique_id
#     if player_2_3_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_3_player_name
#         team_unique_ids_2.iloc[0] = player_1_3_unique_id
#
#     player_2_3_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 4
#     player_2_4_value = player_1_4_unique_id
#     if player_2_4_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_4_player_name
#         team_unique_ids_2.iloc[0] = player_1_4_unique_id
#
#     player_2_4_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 5
#     player_2_5_value = player_1_1_unique_id
#     if player_2_5_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_5_player_name
#         team_unique_ids_2.iloc[0] = player_1_5_unique_id
#
#     player_2_5_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 6
#     player_2_6_value = player_1_6_unique_id
#     if player_2_6_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_6_player_name
#         team_unique_ids_2.iloc[0] = player_1_6_unique_id
#
#     player_2_6_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 7
#     player_2_7_value = player_1_7_unique_id
#     if player_2_1_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_7_player_name
#         team_unique_ids_2.iloc[0] = player_1_7_unique_id
#
#     player_2_7_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 8
#     player_2_8_value = player_1_8_unique_id
#     if player_2_8_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_8_player_name
#         team_unique_ids_2.iloc[0] = player_1_8_unique_id
#
#     player_2_8_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 9
#     player_2_9_value = player_1_9_unique_id
#     if player_2_9_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_9_player_name
#         team_unique_ids_2.iloc[0] = player_1_9_unique_id
#
#     player_2_9_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 10
#     player_2_10_value = player_1_10_unique_id
#     if player_2_10_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_10_player_name
#         team_unique_ids_2.iloc[0] = player_1_10_unique_id
#
#     player_2_10_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 11
#     player_2_11_value = player_1_11_unique_id
#     if player_2_11_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_11_player_name
#         team_unique_ids_2.iloc[0] = player_1_11_unique_id
#
#     player_2_11_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 12
#     player_2_12_value = player_1_12_unique_id
#     if player_2_12_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_12_player_name
#         team_unique_ids_2.iloc[0] = player_1_12_unique_id
#
#     player_2_12_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 13
#     player_2_13_value = player_1_13_unique_id
#     if player_2_13_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_13_player_name
#         team_unique_ids_2.iloc[0] = player_1_13_unique_id
#
#     player_2_13_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 14
#     player_2_14_value = player_1_14_unique_id
#     if player_2_1_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_14_player_name
#         team_unique_ids_2.iloc[0] = player_1_14_unique_id
#
#     player_2_14_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     #Player 15
#     player_2_15_value = player_1_15_unique_id
#     if player_2_1_value not in team_unique_ids_2.unique():
#         team_names_2.iloc[0] = player_1_15_player_name
#         team_unique_ids_2.iloc[0] = player_1_15_unique_id
#
#     player_2_15_option = [{'label': name, 'value': team_unique_ids_2[i]} for i, name in enumerate(team_names_2)]
#
#     team_names_json_2 = team_names_2.to_json(date_format='iso', orient='split')
#     team_unique_ids_json_2 = team_unique_ids_2.to_json(date_format='iso', orient='split')
#
#
#     return (player_1_1_value, player_1_1_position, player_1_1_team_code, player_1_1_opposition[0], player_1_1_was_home[0], player_1_1_odds_win[0], player_1_1_player_form[0], player_1_1_opposition[1], player_1_1_was_home[1], player_1_1_odds_win[1], player_1_1_player_form[1],
#             player_1_2_value, player_1_2_position, player_1_2_team_code, player_1_2_opposition[0], player_1_2_was_home[0], player_1_2_odds_win[0], player_1_2_player_form[0], player_1_2_opposition[1], player_1_2_was_home[1], player_1_2_odds_win[1], player_1_2_player_form[1],
#             player_1_3_value, player_1_3_position, player_1_3_team_code, player_1_3_opposition[0], player_1_3_was_home[0], player_1_3_odds_win[0], player_1_3_player_form[0], player_1_3_opposition[1], player_1_3_was_home[1], player_1_3_odds_win[1], player_1_3_player_form[1],
#             player_1_4_value, player_1_4_position, player_1_4_team_code, player_1_4_opposition[0], player_1_4_was_home[0], player_1_4_odds_win[0], player_1_4_player_form[0], player_1_4_opposition[1], player_1_4_was_home[1], player_1_4_odds_win[1], player_1_4_player_form[1],
#             player_1_5_value, player_1_5_position, player_1_5_team_code, player_1_5_opposition[0], player_1_5_was_home[0], player_1_5_odds_win[0], player_1_5_player_form[0], player_1_5_opposition[1], player_1_5_was_home[1], player_1_5_odds_win[1], player_1_5_player_form[1],
#             player_1_6_value, player_1_6_position, player_1_6_team_code, player_1_6_opposition[0], player_1_6_was_home[0], player_1_6_odds_win[0], player_1_6_player_form[0], player_1_6_opposition[1], player_1_6_was_home[1], player_1_6_odds_win[1], player_1_6_player_form[1],
#             player_1_7_value, player_1_7_position, player_1_7_team_code, player_1_7_opposition[0], player_1_7_was_home[0], player_1_7_odds_win[0], player_1_7_player_form[0], player_1_7_opposition[1], player_1_7_was_home[1], player_1_7_odds_win[1], player_1_7_player_form[1],
#             player_1_8_value, player_1_8_position, player_1_8_team_code, player_1_8_opposition[0], player_1_8_was_home[0], player_1_8_odds_win[0], player_1_8_player_form[0], player_1_8_opposition[1], player_1_8_was_home[1], player_1_8_odds_win[1], player_1_8_player_form[1],
#             player_1_9_value, player_1_9_position, player_1_9_team_code, player_1_9_opposition[0], player_1_9_was_home[0], player_1_9_odds_win[0], player_1_9_player_form[0], player_1_9_opposition[1], player_1_9_was_home[1], player_1_9_odds_win[1], player_1_9_player_form[1],
#             player_1_10_value, player_1_10_position, player_1_10_team_code, player_1_10_opposition[0], player_1_10_was_home[0], player_1_10_odds_win[0], player_1_10_player_form[0], player_1_10_opposition[1], player_1_10_was_home[1], player_1_10_odds_win[1], player_1_10_player_form[1],
#             player_1_11_value, player_1_11_position, player_1_11_team_code, player_1_11_opposition[0], player_1_11_was_home[0], player_1_11_odds_win[0], player_1_11_player_form[0], player_1_11_opposition[1], player_1_11_was_home[1], player_1_11_odds_win[1], player_1_11_player_form[1],
#             player_1_12_value, player_1_12_position, player_1_12_team_code, player_1_12_opposition[0], player_1_12_was_home[0], player_1_12_odds_win[0], player_1_12_player_form[0], player_1_12_opposition[1], player_1_12_was_home[1], player_1_12_odds_win[1], player_1_12_player_form[1],
#             player_1_13_value, player_1_13_position, player_1_13_team_code, player_1_13_opposition[0], player_1_13_was_home[0], player_1_13_odds_win[0], player_1_13_player_form[0], player_1_13_opposition[1], player_1_13_was_home[1], player_1_13_odds_win[1], player_1_13_player_form[1],
#             player_1_14_value, player_1_14_position, player_1_14_team_code, player_1_14_opposition[0], player_1_14_was_home[0], player_1_14_odds_win[0], player_1_14_player_form[0], player_1_14_opposition[1], player_1_14_was_home[1], player_1_14_odds_win[1], player_1_14_player_form[1],
#             player_1_15_value, player_1_15_position, player_1_15_team_code, player_1_15_opposition[0], player_1_15_was_home[0], player_1_15_odds_win[0], player_1_15_player_form[0], player_1_15_opposition[1], player_1_15_was_home[1], player_1_15_odds_win[1], player_1_15_player_form[1],
#             player_2_1_option, player_2_1_value,
#             player_2_2_option, player_2_2_value,
#             player_2_3_option, player_2_3_value,
#             player_2_4_option, player_2_4_value,
#             player_2_5_option, player_2_5_value,
#             player_2_6_option, player_2_6_value,
#             player_2_7_option, player_2_7_value,
#             player_2_8_option, player_2_8_value,
#             player_2_9_option, player_2_9_value,
#             player_2_10_option, player_2_10_value,
#             player_2_11_option, player_2_11_value,
#             player_2_12_option, player_2_12_value,
#             player_2_13_option, player_2_13_value,
#             player_2_14_option, player_2_14_value,
#             player_2_15_option, player_2_15_value,
#             team_names_json_1, team_unique_ids_json_1, team_names_json_2, team_unique_ids_json_2)



@app.callback(
    [Output('player_1_1_name', 'options')],
    [Input('player_1_1_transfer', 'value')],
    [State('intermediate-team_names_gw1', 'children'),
     State('intermediate-team_unique_ids_gw1', 'children'),
     State('data2020-unique-ids-stored-json', 'children'),
     State('data2020-names-stored-json', 'children')],
)
def select_transfers_gw1_p1(transfer_tick,
                             team_names_json,
                             team_unique_ids_json,
                             players_2020_unique_ids_json,
                             players_2020_names_json):

    players_2020_names = list(pd.read_json(players_2020_names_json, orient='split', typ='series').values)
    players_2020_unique_ids = list(pd.read_json(players_2020_unique_ids_json, orient='split', typ='series'))

    #GW + 1
    team_names = pd.read_json(team_names_json, orient='split', typ='series')
    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')

    if transfer_tick != None:
        if len(transfer_tick) > 0:
            player_options = [[{'label': name, 'value': players_2020_unique_ids[i]} for i, name in enumerate(players_2020_names)]]
        else:
            player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    else:
        player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    return (player_options)


@app.callback(
    [Output('player_2_1_name', 'options')],
    [Input('player_2_1_transfer', 'value')],
    [State('intermediate-team_names_gw2', 'children'),
     State('intermediate-team_unique_ids_gw2', 'children'),
     State('data2020-unique-ids-stored-json', 'children'),
     State('data2020-names-stored-json', 'children')],
)
def select_transfers_gw2_p1(transfer_tick,
                             team_names_json,
                             team_unique_ids_json,
                             players_2020_unique_ids_json,
                             players_2020_names_json):

    players_2020_names = list(pd.read_json(players_2020_names_json, orient='split', typ='series').values)
    players_2020_unique_ids = list(pd.read_json(players_2020_unique_ids_json, orient='split', typ='series'))

    #GW + 1
    team_names = pd.read_json(team_names_json, orient='split', typ='series')
    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')

    if transfer_tick != None:
        if len(transfer_tick) > 0:
            player_options = [[{'label': name, 'value': players_2020_unique_ids[i]} for i, name in enumerate(players_2020_names)]]
        else:
            player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    else:
        player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    return (player_options)


@app.callback(
    [Output('player_3_1_name', 'options')],
    [Input('player_3_1_transfer', 'value')],
    [State('intermediate-team_names_gw3', 'children'),
     State('intermediate-team_unique_ids_gw3', 'children'),
     State('data2020-unique-ids-stored-json', 'children'),
     State('data2020-names-stored-json', 'children')],
)
def select_transfers_gw3_p1(transfer_tick,
                             team_names_json,
                             team_unique_ids_json,
                             players_2020_unique_ids_json,
                             players_2020_names_json):

    players_2020_names = list(pd.read_json(players_2020_names_json, orient='split', typ='series').values)
    players_2020_unique_ids = list(pd.read_json(players_2020_unique_ids_json, orient='split', typ='series'))

    #GW + 1
    team_names = pd.read_json(team_names_json, orient='split', typ='series')
    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')

    if transfer_tick != None:
        if len(transfer_tick) > 0:
            player_options = [[{'label': name, 'value': players_2020_unique_ids[i]} for i, name in enumerate(players_2020_names)]]
        else:
            player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    else:
        player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    return (player_options)


@app.callback(
    [Output('player_4_1_name', 'options')],
    [Input('player_4_1_transfer', 'value')],
    [State('intermediate-team_names_gw4', 'children'),
     State('intermediate-team_unique_ids_gw4', 'children'),
     State('data2020-unique-ids-stored-json', 'children'),
     State('data2020-names-stored-json', 'children')],
)
def select_transfers_gw4_p1(transfer_tick,
                             team_names_json,
                             team_unique_ids_json,
                             players_2020_unique_ids_json,
                             players_2020_names_json):

    players_2020_names = list(pd.read_json(players_2020_names_json, orient='split', typ='series').values)
    players_2020_unique_ids = list(pd.read_json(players_2020_unique_ids_json, orient='split', typ='series'))

    #GW + 1
    team_names = pd.read_json(team_names_json, orient='split', typ='series')
    team_unique_ids = pd.read_json(team_unique_ids_json, orient='split', typ='series')

    if transfer_tick != None:
        if len(transfer_tick) > 0:
            player_options = [[{'label': name, 'value': players_2020_unique_ids[i]} for i, name in enumerate(players_2020_names)]]
        else:
            player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    else:
        player_options = [[{'label': name, 'value': team_unique_ids[i]} for i, name in enumerate(team_names)]]

    return (player_options)


@app.callback(
    [Output('IPA_indicator_form', 'figure'),
     Output('IPA_indicator_totalpoints', 'figure'),
     Output('IPA_indicator_ICT', 'figure'),
     Output('IPA_indicator_prob', 'figure'),
     Output('IPL_histogram', 'figure'),
     Output('IPL_round_subplots', 'figure'),
     Output('IPL_position', 'children'),
     Output('IPL_team', 'children'),
     Output('IPL_value', 'children'),
     Output('IPL_selected', 'children'),
     Output('IPL_FTP', 'children'),
     Output('IPL_news', 'children'),
     Output('IPL_player_picture', 'children'),
     Output('IPL_position_reference', 'children'),
     Output('IPL_team_reference', 'children'),
     Output('IPL_value_reference', 'children'),
     Output('IPL_selected_reference', 'children'),
     Output('IPL_FTP_reference', 'children'),
     Output('IPL_news_reference', 'children')],
    [Input('IPL_playerselect', 'value'),
     Input('IPL_reference_player', 'value')],
)
def IPL_select_player(unique_id,
                      unique_id_reference):


    # Player Data
    data_IPL_player = data[data['unique_id']==unique_id]
    round_max = data_IPL_player['round'].max()

    element_id = determine_element_id(data, unique_id, season_latest)

    # Get the maximum number of fpl players
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    r = requests.get(url)
    json = r.json()
    total_players = int(json['total_players'])
    element_data = pd.DataFrame(json['elements'])

    element_type = data_IPL_player[data_IPL_player['round']==round_max]['element_type'].values[0]
    element_position = element_type2position(element_type)
    element_team = data_IPL_player[data_IPL_player['round']==round_max]['team_name']
    element_value = '£' + str(data_IPL_player[data_IPL_player['round']==round_max]['value'].values[0]/10)
    element_selected_temp = float((data_IPL_player[data_IPL_player["round"]==round_max]["selected"]/total_players)*100)
    element_selected = '{0:.1f}'.format(element_selected_temp) + '%'
    if element_data[element_data['id']==element_id]['chance_of_playing_next_round'].isnull().values.any() == False:
        element_FTP = str(element_data[element_data['id']==element_id]['chance_of_playing_next_round'].values[0]) + '%'
    else:
        element_FTP = str(100) + '%'
    element_news = element_data[element_data['id']==element_id]['news'].values[0]
    element_photo = element_data[element_data['id']==element_id]['photo'].values[0][:-4]
    element_photo += '.png'

    # Reference Player Data
    data_IPL_player_reference = data[data['unique_id']==unique_id_reference]
    round_max_reference = data_IPL_player_reference['round'].max()

    element_id_reference = determine_element_id(data, unique_id_reference, season_latest)


    element_type_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['element_type'].values[0]

    element_position_reference = element_type2position(element_type_reference)
    element_team_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['team_name']
    element_value_reference = '£' + str(data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['value'].values[0]/10)
    element_selected_temp = float((data_IPL_player_reference[data_IPL_player_reference["round"]==round_max_reference]["selected"]/total_players)*100)
    element_selected_reference = '{0:.1f}'.format(element_selected_temp) + '%'
    if element_data[element_data['id']==element_id_reference]['chance_of_playing_next_round'].isnull().values.any() == False:
        element_FTP_reference = str(element_data[element_data['id']==element_id_reference]['chance_of_playing_next_round'].values[0]) + '%'
    else:
        element_FTP_reference = str(100) + '%'
    element_news_reference = element_data[element_data['id']==element_id_reference]['news'].values[0]

    ######## Dash indicators ########

    # Form

    indicator_form = go.Figure()

    max_form_all = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_total_points_any_4'].max()
    max_form_home = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_total_points_home_4'].max()
    max_form_away = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_total_points_away_4'].max()

    form_all = data_IPL_player[data_IPL_player['round']==round_max]['mean_total_points_any_4'].values[0]
    form_all_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_total_points_any_4'].values[0]

    if round_max > 1:
        form_all_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_total_points_any_4'].values[0]
    else:
        form_all_previous = 0

    form_home = data_IPL_player[data_IPL_player['round']==round_max]['mean_total_points_home_4'].values[0]
    form_home_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_total_points_home_4'].values[0]

    if round_max > 1:
        form_home_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_total_points_home_4'].values[0]
    else:
        form_home_previous = 0

    form_away = data_IPL_player[data_IPL_player['round']==round_max]['mean_total_points_away_4'].values[0]
    form_away_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_total_points_away_4'].values[0]

    if round_max > 1:
        form_away_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_total_points_away_4'].values[0]
    else:
        form_away_previous = 0

    indicator_form.add_trace(go.Indicator(
        value = form_all,
        delta = {'reference': form_all_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_form_all]},
            'steps': [{'range': [0, form_all_reference], 'color': 'lightblue'}]},
        title = {'text': "Overall"},
        domain = {'row': 0, 'column': 0}))

    indicator_form.add_trace(go.Indicator(
        value = form_home,
        delta = {'reference': form_home_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_form_home]},
            'steps': [{'range': [0, form_home_reference], 'color': 'lightblue'}]},
        title = {'text': "Home"},
        domain = {'row': 0, 'column': 1}))

    indicator_form.add_trace(go.Indicator(
        value = form_away,
        delta = {'reference': form_away_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_form_away]},
            'steps': [{'range': [0, form_away_reference], 'color': 'lightblue'}]},
        title = {'text': "Away"},
        domain = {'row': 0, 'column': 2}))

    indicator_form.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        height = 180,
        template = {'data' : {'indicator': [{

            'mode' : "number+delta+gauge",
            'delta' : {'reference': 150}}]
                             }})

    indicator_form.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})

    # Total Points

    max_points_all = data[(data['season']==season_latest) & (data['round']==round_max)]['total_total_points_any_all'].max()
    max_points_home = data[(data['season']==season_latest) & (data['round']==round_max)]['total_total_points_home_all'].max()
    max_points_away = data[(data['season']==season_latest) & (data['round']==round_max)]['total_total_points_away_all'].max()

    points_all = data_IPL_player[data_IPL_player['round']==round_max]['total_total_points_any_all'].values[0]
    points_all_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['total_total_points_any_all'].values[0]

    if round_max > 1:
        points_all_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['total_total_points_any_all'].values[0]
    else:
        points_all_previous = 0

    points_home = data_IPL_player[data_IPL_player['round']==round_max]['total_total_points_home_all'].values[0]
    points_home_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['total_total_points_home_all'].values[0]

    if round_max > 1:
        points_home_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['total_total_points_home_all'].values[0]
    else:
        points_home_previous = 0

    points_away = data_IPL_player[data_IPL_player['round']==round_max]['total_total_points_away_all'].values[0]
    points_away_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['total_total_points_away_all'].values[0]

    if round_max > 1:
        points_away_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['total_total_points_away_all'].values[0]
    else:
        points_away_previous = 0

    indicator_totalpoints = go.Figure()

    indicator_totalpoints.add_trace(go.Indicator(
        value = points_all,
        delta = {'reference': points_all_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_points_all]},
            'steps': [{'range': [0, points_all_reference], 'color': 'lightblue'}]},
        title = {'text': "Overall"},
        domain = {'row': 0, 'column': 0}))

    indicator_totalpoints.add_trace(go.Indicator(
        value = points_home,
        delta = {'reference': points_home_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_points_home]},
            'steps': [{'range': [0, points_home_reference], 'color': 'lightblue'}]},
        title = {'text': "Home"},
        domain = {'row': 0, 'column': 1}))

    indicator_totalpoints.add_trace(go.Indicator(
        value = points_away,
        delta = {'reference': points_away_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_points_away]},
            'steps': [{'range': [0, points_away_reference], 'color': 'lightblue'}]},
        title = {'text': "Away"},
        domain = {'row': 0, 'column': 2}))

    indicator_totalpoints.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        height = 180,
        template = {'data' : {'indicator': [{

            'mode' : "number+delta+gauge",
            'delta' : {'reference': 90}}]
                             }})

    indicator_totalpoints.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})

    # ICT Index

    max_influence = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_influence_any_all'].max()
    max_creativity = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_creativity_any_all'].max()
    max_threat = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_threat_any_all'].max()
    max_ICT = data[(data['season']==season_latest) & (data['round']==round_max)]['mean_ict_index_any_all'].max()

    influence = data_IPL_player[data_IPL_player['round']==round_max]['mean_influence_any_all'].values[0]
    influence_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_influence_any_all'].values[0]

    if round_max > 1:
        influence_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_influence_any_all'].values[0]
    else:
        influence_previous = 0

    creativity = data_IPL_player[data_IPL_player['round']==round_max]['mean_creativity_any_all'].values[0]
    creativity_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_creativity_any_all'].values[0]

    if round_max > 1:
        creativity_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_creativity_any_all'].values[0]
    else:
        creativity_previous = 0

    threat = data_IPL_player[data_IPL_player['round']==round_max]['mean_threat_any_all'].values[0]
    threat_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_threat_any_all'].values[0]

    if round_max > 1:
        threat_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_threat_any_all'].values[0]
    else:
        threat_previous = 0

    ICT = data_IPL_player_reference[data_IPL_player_reference['round']==round_max]['mean_ict_index_any_all'].values[0]
    ICT_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['mean_ict_index_any_all'].values[0]

    if round_max > 1:
        ICT_previous = data_IPL_player[data_IPL_player['round']==round_max-1]['mean_ict_index_any_all'].values[0]
    else:
        ICT_previous = 0

    indicator_ICT = go.Figure()

    indicator_ICT.add_trace(go.Indicator(
        value = influence,
        delta = {'reference': influence_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_influence]},
            'steps': [{'range': [0, influence_reference], 'color': 'lightblue'}]},
        title = {'text': "Influence"},
        domain = {'row': 0, 'column': 1}))

    indicator_ICT.add_trace(go.Indicator(
        value = creativity,
        delta = {'reference': creativity_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_creativity]},
            'steps': [{'range': [0, creativity_reference], 'color': 'lightblue'}]},
        title = {'text': "Creativity"},
        domain = {'row': 0, 'column': 2}))

    indicator_ICT.add_trace(go.Indicator(
        value = threat,
        delta = {'reference': threat_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_threat]},
            'steps': [{'range': [0, threat_reference], 'color': 'lightblue'}]},
        title = {'text': "Threat"},
        domain = {'row': 0, 'column': 3}))

    indicator_ICT.add_trace(go.Indicator(
        value = ICT,
        delta = {'reference': ICT_previous},
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_ICT]},
            'steps': [{'range': [0, ICT_reference], 'color': 'lightblue'}]},
        title = {'text': "ICT"},
        domain = {'row': 0, 'column': 0}))

    indicator_ICT.update_layout(
        grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
        height = 155,
        template = {'data' : {'indicator': [{

            'mode' : "number+delta+gauge",
            'delta' : {'reference': 90}}]
                             }})

    indicator_ICT.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})

    # Probabilities

    max_prob_goal = 1
    max_prob_assist = 1
    max_prob_clean_sheet = 1
    max_prob_minutes = 1

    prob_goal = data_IPL_player[data_IPL_player['round']==round_max]['prob_occur_goals_scored_greater_than_0__any_all'].values[0]
    prob_goal_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['prob_occur_goals_scored_greater_than_0__any_all'].values[0]

    prob_assist = data_IPL_player[data_IPL_player['round']==round_max]['prob_occur_assists_greater_than_0__any_all'].values[0]
    prob_assist_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['prob_occur_assists_greater_than_0__any_all'].values[0]

    prob_clean_sheet = data_IPL_player[data_IPL_player['round']==round_max]['prob_occur_clean_sheets_greater_than_0__any_all'].values[0]
    prob_clean_sheet_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['prob_occur_clean_sheets_greater_than_0__any_all'].values[0]

    prob_minutes = data_IPL_player[data_IPL_player['round']==round_max]['prob_occur_minutes_greater_than_0__any_all'].values[0]
    prob_minutes_reference = data_IPL_player_reference[data_IPL_player_reference['round']==round_max_reference]['prob_occur_minutes_greater_than_0__any_all'].values[0]

    indicator_prob = go.Figure()

    indicator_prob.add_trace(go.Indicator(
        value = prob_goal,
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_prob_goal]},
            'steps': [{'range': [0, prob_goal_reference], 'color': 'lightblue'}]},
        title = {'text': "Goal"},
        domain = {'row': 0, 'column': 0}))

    indicator_prob.add_trace(go.Indicator(
        value = prob_assist,
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_prob_assist]},
            'steps': [{'range': [0, prob_assist_reference], 'color': 'lightblue'}]},
        title = {'text': "Assist"},
        domain = {'row': 0, 'column': 1}))

    indicator_prob.add_trace(go.Indicator(
        value = prob_clean_sheet,
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_prob_clean_sheet]},
            'steps': [{'range': [0, prob_clean_sheet_reference], 'color': 'lightblue'}]},
        title = {'text': "Clean Sheet"},
        domain = {'row': 0, 'column': 2}))

    indicator_prob.add_trace(go.Indicator(
        value = prob_minutes,
        gauge = {
            'bar': {'color': "darkblue"},
            'axis': {'range': [None, max_prob_minutes]},
            'steps': [{'range': [0, prob_minutes_reference], 'color': 'lightblue'}]},
        title = {'text': "Playing"},
        domain = {'row': 0, 'column': 3}))

    indicator_prob.update_layout(
        grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
        height = 155,
        template = {'data' : {'indicator': [{

            'mode' : "number+gauge"}]
                             }})

    indicator_prob.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})


    # Histogram
    round_max_overall = data[data['season']==season_latest].max()
    # print(round_max_overall)
    # points_histogram = px.histogram(data[(data['season']==2020) & (data['round']==round_max)], x="total_points", nbins=50)
    points_histogram = go.Figure(data=[go.Histogram(x=data[(data['season']==season_latest) & (data['round']==round_max)]['total_total_points_any_all'], histnorm='probability', nbinsx=50, marker_color='lightgray')])

    points_histogram.add_shape(
            go.layout.Shape(type='line', xref='x', yref='y',
                            x0=points_all, y0=0, x1=points_all, y1=1, line={'dash': 'dash', 'color': 'darkblue'}))

    points_histogram.add_shape(
            go.layout.Shape(type='line', xref='x', yref='y',
                            x0=points_all_reference, y0=0, x1=points_all_reference, y1=1, line={'dash': 'dash', 'color': 'lightblue'}))

    IPL_subplots = make_subplots(rows=2, cols=3)

    if element_type == 1:
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['total_points'], marker_color='darkblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['total_points'], marker_color='lightblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['clean_sheets'], marker_color='darkblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['clean_sheets'], marker_color='lightblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['bonus'], marker_color='darkblue'),1, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['bonus'], marker_color='lightblue'),1, 3)

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['goals_conceded'], marker_color='darkblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['goals_conceded'], marker_color='lightblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['saves'], marker_color='darkblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['saves'], marker_color='lightblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['minutes'], marker_color='darkblue'),2, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['minutes'], marker_color='lightblue'),2, 3)

        IPL_subplots['layout']['xaxis']['title']='Round'
        IPL_subplots['layout']['xaxis2']['title']='Round'
        IPL_subplots['layout']['xaxis3']['title']='Round'
        IPL_subplots['layout']['xaxis4']['title']='Round'
        IPL_subplots['layout']['xaxis5']['title']='Round'
        IPL_subplots['layout']['xaxis6']['title']='Round'

        IPL_subplots['layout']['yaxis']['title']='Points'
        IPL_subplots['layout']['yaxis2']['title']='Clean Sheets'
        IPL_subplots['layout']['yaxis3']['title']='Bonus Points'
        IPL_subplots['layout']['yaxis4']['title']='Goals Conceded'
        IPL_subplots['layout']['yaxis5']['title']='Saves'
        IPL_subplots['layout']['yaxis6']['title']='Minutes Played'

    elif element_type == 2:

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['total_points'], marker_color='darkblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['total_points'], marker_color='lightblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['goals_scored'], marker_color='darkblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['goals_scored'], marker_color='lightblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['assists'], marker_color='darkblue'),1, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['assists'], marker_color='lightblue'),1, 3)

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['bonus'], marker_color='darkblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['bonus'], marker_color='lightblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['clean_sheets'], marker_color='darkblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['clean_sheets'], marker_color='lightblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['minutes'], marker_color='darkblue'),2, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['minutes'], marker_color='lightblue'),2, 3)

        IPL_subplots['layout']['xaxis']['title']='Round'
        IPL_subplots['layout']['xaxis2']['title']='Round'
        IPL_subplots['layout']['xaxis3']['title']='Round'
        IPL_subplots['layout']['xaxis4']['title']='Round'
        IPL_subplots['layout']['xaxis5']['title']='Round'
        IPL_subplots['layout']['xaxis6']['title']='Round'

        IPL_subplots['layout']['yaxis']['title']='Points'
        IPL_subplots['layout']['yaxis2']['title']='Goals Scored'
        IPL_subplots['layout']['yaxis3']['title']='Assists'
        IPL_subplots['layout']['yaxis4']['title']='Bonus Points'
        IPL_subplots['layout']['yaxis5']['title']='Clean Sheets'
        IPL_subplots['layout']['yaxis6']['title']='Minutes Played'

    elif element_type == 3:

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['total_points'], marker_color='darkblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['total_points'], marker_color='lightblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['goals_scored'], marker_color='darkblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['goals_scored'], marker_color='lightblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['assists'], marker_color='darkblue'),1, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['assists'], marker_color='lightblue'),1, 3)

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['bonus'], marker_color='darkblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['bonus'], marker_color='lightblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['clean_sheets'], marker_color='darkblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['clean_sheets'], marker_color='lightblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['minutes'], marker_color='darkblue'),2, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['minutes'], marker_color='lightblue'),2, 3)

        IPL_subplots['layout']['xaxis']['title']='Round'
        IPL_subplots['layout']['xaxis2']['title']='Round'
        IPL_subplots['layout']['xaxis3']['title']='Round'
        IPL_subplots['layout']['xaxis4']['title']='Round'
        IPL_subplots['layout']['xaxis5']['title']='Round'
        IPL_subplots['layout']['xaxis6']['title']='Round'

        IPL_subplots['layout']['yaxis']['title']='Points'
        IPL_subplots['layout']['yaxis2']['title']='Goals Scored'
        IPL_subplots['layout']['yaxis3']['title']='Assists'
        IPL_subplots['layout']['yaxis4']['title']='Bonus Points'
        IPL_subplots['layout']['yaxis5']['title']='Clean Sheets'
        IPL_subplots['layout']['yaxis6']['title']='Minutes Played'

    else:

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['total_points'], marker_color='darkblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['total_points'], marker_color='lightblue'), 1, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['goals_scored'], marker_color='darkblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['goals_scored'], marker_color='lightblue'), 1, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['assists'], marker_color='darkblue'),1, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['assists'], marker_color='lightblue'),1, 3)

        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['bonus'], marker_color='darkblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['bonus'], marker_color='lightblue'), 2, 1)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['ict_index'], marker_color='darkblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['ict_index'], marker_color='lightblue'), 2, 2)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player['round'], y=data_IPL_player['minutes'], marker_color='darkblue'),2, 3)
        IPL_subplots.add_trace(go.Bar(x=data_IPL_player_reference['round'], y=data_IPL_player_reference['minutes'], marker_color='lightblue'),2, 3)

        IPL_subplots['layout']['xaxis']['title']='Round'
        IPL_subplots['layout']['xaxis2']['title']='Round'
        IPL_subplots['layout']['xaxis3']['title']='Round'
        IPL_subplots['layout']['xaxis4']['title']='Round'
        IPL_subplots['layout']['xaxis5']['title']='Round'
        IPL_subplots['layout']['xaxis6']['title']='Round'

        IPL_subplots['layout']['yaxis']['title']='Points'
        IPL_subplots['layout']['yaxis2']['title']='Goals Scored'
        IPL_subplots['layout']['yaxis3']['title']='Assists'
        IPL_subplots['layout']['yaxis4']['title']='Bonus Points'
        IPL_subplots['layout']['yaxis5']['title']='ICT Index'
        IPL_subplots['layout']['yaxis6']['title']='Minutes Played'

    IPL_subplots.update(layout_showlegend=False)

    IPL_subplots.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})

    player_img = html.Img(src='https://resources.premierleague.com/premierleague/photos/players/110x140/p' + element_photo,style={'width': '90%'})

    return indicator_form, indicator_totalpoints, indicator_ICT, indicator_prob, points_histogram, IPL_subplots, \
           element_position, element_team, element_value, element_selected, element_FTP, element_news, player_img, \
           element_position_reference, element_team_reference, element_value_reference, element_selected_reference, element_FTP_reference, element_news_reference

@app.callback(
    [Output('fig-league_graph', 'figure'),
     Output('table_league', 'data')],
    [Input('input-league_id','value')],
    [State('fig1-xaxis-column','value'),
     State('fig1-yaxis-column','value')])
def update_league(league_id,
                  xaxis_column_name,
                  yaxis_column_name):

    DataLoaderObj = DL.DataLoader()
    DataLoaderObj.scrape_league_standings(path_league_data_full,
                                          path_league_data,
                                          league_id=int(league_id),
                                          league_type='classic')

    data_team_ids_summary = pd.read_csv(path_league_data, encoding='UTF-8')
    data_team_ids_summary = data_team_ids_summary.rename(columns={"id": "identifier", "entry": "id"})
    data_team_ids = data_team_ids_summary.copy()
    data_team_ids = data_team_ids[['rank', 'entry_name', 'total']]
    data_league_standings = pd.read_csv(path_league_data_full, encoding='UTF-8')
    data_league_standings = data_league_standings.merge(data_team_ids_summary.drop(columns=['rank', 'rank_sort']), on=['id'])

    data_filt = data_league_standings.copy()
    data_filt = data_filt[data_filt['round'] <= data_filt['round'].max()]

    fig = px.line(data_filt,
                 x=xaxis_column_name,
                 y=yaxis_column_name,
                 color='entry_name')


    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig, data_team_ids.to_dict('records')


@app.callback(
    Output('fig-league_graph', 'figure'),
    [Input('fig1-xaxis-column','value'),
     Input('fig1-yaxis-column','value')])
def update_league_graph(xaxis_column_name,
                        yaxis_column_name):


    data_filt = data_league_standings.copy()
    data_filt = data_filt[data_filt['round'] <= data_filt['round'].max()]

    fig = px.line(data_filt,
                 x=xaxis_column_name,
                 y=yaxis_column_name,
                 color='entry_name')

    # fig.update(layout_coloraxis_showscale=False)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    # fig.update(layout_coloraxis_showscale=False)

    return fig


@app.callback(
    Output('fig1-aggregate-graph', 'figure'),
    [Input('fig1-plot-type', 'value'),
     Input('fig1-xaxis-column', 'value'),
     Input('fig1-yaxis-column', 'value'),
     Input('fig-aggregate-column', 'value'),
     Input('fig1-errorbar-column', 'value'),
     Input('year-filter', 'value'),
     Input('player-filter', 'value'),
     Input('position-type', 'value'),
     Input('player-selection-type', 'value'),
     Input('n', 'value')])
def update_aggregate_graph(plot_type,
                        xaxis_column_name,
                        yaxis_column_name,
                        aggregate_column_name,
                        errorbar_column_name,
                        season,
                        player_filter,
                        position_type,
                        player_selection_type,
                        n):

    if n != '':
        n = int(n)
    else:
        n = 1



    data_filt = data.copy()
    data_filt = data_filt[data_filt['season']==season]

    element_type = postion2element_type(position_type)

    y_data_error = determine_error_bar(yaxis_column_name, errorbar_column_name)
    if y_data_error is None:
        data_filt['error_none'] = 0
        y_data_error = 'error_none'

    if player_selection_type == 'Top players':
        if element_type != -1:
            data_filt = data_filt[(data_filt['element_type']==element_type)]
        unique_ids = find_top_results(data_filt, target_column=[aggregate_column_name], n=n, element_type=element_type)
    elif player_selection_type == 'Manual':
        unique_ids = []
        if player_filter is not None:
            for player in player_filter:
                unique_ids.append(find_unique_id(data_filt, player.split('_')[0], player.split('_')[1], season))
        else:
            unique_ids.append(-1)

        unique_ids = pd.Series(unique_ids)

    if player_filter is not None:
        if (len(player_filter) == 0) and (player_selection_type == 'Manual'):
            unique_ids = []
            if len(player_filter) > 0:
                for player in player_filter:
                    unique_ids.append(find_unique_id(data_filt, player.split('_')[0], player.split('_')[1], season))
            else:
                unique_ids.append(-1)

            unique_ids = pd.Series(unique_ids)

    if unique_ids.iloc[0] != -1:
        data_filt = data[(data['unique_id'].isin(unique_ids))].sort_values(by=aggregate_column_name, ascending=False)
        # data_filt = data_filt[data_filt['round'] == data_filt['round'].max()]
    else:
        data_filt = pd.DataFrame([[0]*len(data_filt.columns)], columns=data_filt.columns)

    colour_scheme = px.colors.sequential.Blues
    if plot_type == 'Bar':
        if unique_ids.iloc[0] != -1:
            data_filt = data_filt[data_filt['round'] == data_filt['round'].max()]

        fig = px.bar(data_filt,
                     x=xaxis_column_name,
                     y=yaxis_column_name,
                     error_y=y_data_error,
                     color=yaxis_column_name,
                     color_continuous_scale=colour_scheme)

        fig.update_traces(customdata=data_filt['unique_id'], selector=dict(type='bar'))

        fig.update(layout_coloraxis_showscale=False)

        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        fig.update(layout_coloraxis_showscale=False)
    elif plot_type == 'Box':
        fig = px.box(data_filt,
                     x=xaxis_column_name,
                     y=yaxis_column_name,
                     points="all")

        fig.update_traces(customdata=data_filt['unique_id'].unique(), selector=dict(type='box'))

        fig.update(layout_coloraxis_showscale=False)

        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        fig.update(layout_coloraxis_showscale=False)

    return fig


@app.callback(Output('unique_id_clickData', 'children'),
              [Input('fig1-aggregate-graph', 'clickData')],
              [State('unique_id_clickData', 'children')])
def save_data(clickData,
              unique_ids_clickData_json):

    if clickData is not None:
        unique_id = clickData['points'][0]['customdata']
        unique_id_clickData = pd.read_json(unique_ids_clickData_json, orient='split', typ='series')

        if unique_id_clickData is None:
            unique_id_clickData = pd.Series([-1])
        if unique_id not in unique_id_clickData.unique():
            unique_id_clickData = pd.concat([unique_id_clickData, pd.Series([unique_id])])
        else:
            unique_id_clickData = unique_id_clickData[unique_id_clickData!=unique_id]

        return unique_id_clickData.to_json(date_format='iso', orient='split')
    else:
        unique_id_clickData = pd.Series([])
        return unique_id_clickData.to_json(date_format='iso', orient='split')


@app.callback(
    [Output('player-filter', 'options'),
     Output('unique_id_clickData', 'children')],
    [Input('position-type', 'value'),
     Input('player-selection-type', 'value')],
    [State('unique_id_clickData', 'children')])
def update_player_filter(position_type,
                         player_selection_type,
                         unique_ids_clickData_json):

    element_type = postion2element_type(position_type)
    if unique_ids_clickData_json is not None:
        unique_id_clickData = pd.read_json(unique_ids_clickData_json, orient='split', typ='series')
    unique_id_clickData = pd.Series([])


    if element_type > 0:
        data_filt = data.copy()
        data_filt = data_filt[(data_filt['season']==season_latest)]
        return [{'label': i, 'value': i} for i in data_filt.sort_values(by='name_last')[(data_filt['element_type']==element_type)]['name'].unique()], unique_id_clickData.to_json(date_format='iso', orient='split')
    else:
        return [{'label': i, 'value': i} for i in data.sort_values(by='name_last')[data['season']==season_latest]['name'].unique()], unique_id_clickData.to_json(date_format='iso', orient='split')


@app.callback(
    [Output('fig2-points-graph', 'figure'),
     Output('fig2-goals-graph', 'figure'),
     Output('fig2-assists-graph', 'figure')],
    [Input('unique_id_clickData', 'children')],
    [State('fig2-points-yaxis-column', 'value'),
     State('fig2-goals-yaxis-column', 'value'),
     State('fig2-assists-yaxis-column', 'value'),
     State('year-filter', 'value'),
     State('position-type', 'value'),
     State('n', 'value')])
def display_click_data(unique_ids_clickData_json,
                        yaxis_column_name_points,
                        yaxis_column_name_goals,
                        yaxis_column_name_assists,
                        season,
                        position_type,
                        n):

    if unique_ids_clickData_json is not None:
        unique_id_clickData = pd.read_json(unique_ids_clickData_json, orient='split', typ='series')
    else:
        unique_id_clickData = None

    if n != '':
        n = int(n)
    else:
        n = 1

    fig1, fig2, fig3 = update_points_graph_clickData(unique_id_clickData,
                                                    yaxis_column_name_points,
                                                    yaxis_column_name_goals,
                                                    yaxis_column_name_assists,
                                                    season,
                                                    position_type,
                                                    n)
    return fig1, fig2, fig3


def update_points_graph_clickData(unique_id_clickData,
                                yaxis_column_name_points,
                                yaxis_column_name_goals,
                                yaxis_column_name_assists,
                                season,
                                position_type,
                                n):

    if n != '':
        n = int(n)
    else:
        n = 1

    xaxis_column_name = 'round'

    data_filt = data.copy()
    data_filt = data_filt[data_filt['season']==season]

    element_type = postion2element_type(position_type)

    unique_ids = pd.Series(unique_id_clickData)
    if unique_ids.shape[0] > 0:
        data_filt = data[(data['unique_id'].isin(unique_ids))].sort_values(by='round')
    else:
        data_filt = pd.DataFrame([[0]*len(data_filt.columns)], columns=data_filt.columns)

    # Update the points graph
    fig1 = px.line(data_filt,
                  x=xaxis_column_name,
                  y=yaxis_column_name_points,
                  hover_name=data_filt['name_last'],
                  color="name_last",
                  color_discrete_sequence=px.colors.qualitative.Dark24)

    fig1.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig1.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
    fig1.update_traces(mode='lines+markers')
    fig1.update_traces(marker=dict(size=8,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))

    # Update plot 2
    fig2 = px.line(data_filt,
                  x=xaxis_column_name,
                  y=yaxis_column_name_goals,
                  hover_name=data_filt['name_last'],
                  color="name_last",
                  color_discrete_sequence=px.colors.qualitative.Dark24)

    fig2.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig2.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
    fig2.update_traces(mode='lines+markers')
    fig2.update_traces(marker=dict(size=8,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))

    # Update plot 3
    fig3 = px.line(data_filt,
                  x=xaxis_column_name,
                  y=yaxis_column_name_assists,
                  hover_name=data_filt['name_last'],
                  color="name_last",
                  color_discrete_sequence=px.colors.qualitative.Dark24)

    fig3.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    fig3.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
    fig3.update_traces(mode='lines+markers')
    fig3.update_traces(marker=dict(size=8,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))

    return fig1, fig2, fig3


def determine_error_bar(y_data, error_bar_type):

    y_data_type = y_data.split('_')[0]
    label = y_data.split('_')[1:]

    if error_bar_type == 'Standard Deviation':
        error_bar_type = 'std'
    elif error_bar_type == 'Standard Error':
        error_bar_type = 'se'

    if y_data_type == 'mean':
        y_data_error_list = [error_bar_type] + label
        y_data_error = ''
        for item in y_data_error_list:
            y_data_error = y_data_error + '_' + item
        y_data_error = y_data_error[1:]

    else:
        y_data_error = None

    return y_data_error



@app.callback(
    [Output('fig1-yaxis-column', 'value')],
    [Input('fig-aggregate-column', 'value')],
    [State('fig1-yaxis-column', 'value')])
def update_aggregate_figure_ycol(fig_aggregate_column,
                                fig1_yaxis_column):

    if fig_aggregate_column is not None:
        return [fig_aggregate_column]
    else:
        return [fig1_yaxis_column]


@app.callback(
    Output('fig1-aggregate-graph', 'fig'),
    [Input('fig1-yaxis-column', 'value'),
     Input('fig1-errorbar-column', 'value')],
    [State('fig1-aggregate-graph', 'fig')])
def update_aggregate_figure_ycol_error(fig_yaxis_column,
                                        fig1_errorbar_column,
                                        fig):

    y_data_error = determine_error_bar(fig_yaxis_column, fig1_errorbar_column)
    if fig is not None:
        fig.update(error_y=y_data_error)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
