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
from flask_caching import Cache
import os
import functools
import unidecode

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


def calculate_player_points(player_form_1, player_form_2, player_cpt, triple_captain=False):

    try:
        player_form_1 = float(player_form_1)
    except:
        player_form_1 = 0

    try:
        player_form_2 = float(player_form_2)
    except:
        player_form_2 = 0

    total_points = player_form_1 + player_form_2

    if player_cpt[0] == 'CPT' and triple_captain is False:
        total_points = total_points * 2

    if player_cpt[0] == 'CPT' and triple_captain is True:
        total_points = total_points * 3

    return total_points


def calculate_team_points(player_form_g1,
                          player_form_g2,
                          player_cpt,
                          gw_tokens):

    player_points = []

    if 'triple-captain' in gw_tokens:
        triple_captain = True
    else:
        triple_captain = False

    for i in range(len(player_form_g1)):
        player_points.append(calculate_player_points(player_form_g1[i], player_form_g2[i], player_cpt[i], triple_captain))

    points_first_team = np.sum(player_points[:11])
    points_subs = np.sum(player_points[11:])

    return points_first_team, points_subs


def calculate_transfer_points(player_trn_list,
                              transfer_free,
                              wildcard):

    total_transfers = 0

    for player_trn in player_trn_list:
        if player_trn is not None:
            total_transfers += 1

    transfer_points = (total_transfers - int(transfer_free)) * -4

    if transfer_points > 0:
        transfer_points = 0

    if len(wildcard) > 0:
        if wildcard[0] == 'wildcard':
            transfer_points = 0

    return transfer_points


def calculate_team_cost(player_value_list):

    team_value = 0

    for player_value in player_value_list:
        team_value += float(player_value)

    return team_value


######################################################################################################################
################################################ Load Data ###########################################################
######################################################################################################################

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_database.csv')
path_player_metadata = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_metadata.csv')
path_team_metadata = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'team_metadata.csv')
path_team_codes = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'team_codes.csv')
path_fixtures = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Data', '2020-21','fixtures.csv')

data = pd.read_csv(path_data)
player_metadata = pd.read_csv(path_player_metadata)
team_metadata = pd.read_csv(path_team_metadata)
team_codes = pd.read_csv(path_team_codes)
fixture_data = pd.read_csv(path_fixtures)

data['mean_total_points_any_3/pound'] = data['mean_total_points_any_3'] / (data['value'] / 10)
data['mean_total_points_any_5/pound'] = data['mean_total_points_any_5'] / (data['value'] / 10)
data['total_total_points_any_all/pound'] = data['total_total_points_any_all'] / (data['value'] / 10)
data['name_first'] = data['name'].str.split('_', expand=True)[0]
data['name_last'] = data['name'].str.split('_', expand=True)[1].str.slice(start=0, stop=20)

path_league_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_standings_full.csv')
path_league_data_full = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Cache', 'league_data_full.csv')
available_indicators_all = data.columns
available_indicators = ['assists', 'bonus', 'bps', 'clean_sheets', 'creativity', 'element', 'element_type', 'fixture', 'goals_conceded', 'goals_scored', 'ict_index', 'influence', 'kickoff_time', 'minutes', 'own_goals', 'penalties_missed', 'penalties_saved', 'red_cards', 'round', 'saves', 'selected', 'team_a_score', 'team_h_score', 'threat', 'total_points', 'transfers_balance', 'transfers_in', 'transfers_out', 'value', 'was_home', 'yellow_cards']

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

league_ids = ['1217918', '1218670', '342405']
league_names = ['The league of Leith', 'The old office Vs no AI', 'Cairn Energy Primera Liga']

email = 'speeder1987@gmail.com'
password = 'Footb@ll2020'
team_id = '5403039'
team_picks = DataLoaderObj.scrape_team_information(email, password, team_id)
transfers = DataLoaderObj.scrape_transfer_information(email, password, team_id)

initial_teamvalue = (team_picks['selling_price'].sum() + transfers['bank'])/10


######################################################################################################################
################################################ Layout Function #####################################################
######################################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
# cache = Cache(app.server, config={
#     # try 'filesystem' if you don't want to setup redis
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
# })
#
# app.config.suppress_callback_exceptions = True

server = app.server


app.layout = html.Div([
    dcc.Tabs(id='tabs-example', value='PA', children=[
        dcc.Tab(label='Player Analysis', value='PA'),
        dcc.Tab(label='FPL League Analysis', value='LA'),
    ]),
    html.Div(id='tabs-example-content'),
])

debug_mode = True

timeout = 300

# Get list of player names and associated unique id's

season_latest = player_metadata['season'].max()
# season_latest = 2020
player_metadata_season = player_metadata[player_metadata['season'] == season_latest]
round_curr = 19
round_next = round_curr + 1

player_names = []
unique_ids = []

for i in range(player_metadata_season.shape[0]):
    player_name_key = player_metadata_season['name'].iloc[i]
    player_name = unidecode.unidecode(player_metadata_season['name_first'].iloc[i]) + ' ' + unidecode.unidecode(player_metadata_season['name_last'].iloc[i])
    unique_id = player_metadata_season['unique_id'].iloc[i]
    player_names.append(player_name)
    unique_ids.append(unique_id)

players_2020_names_json = pd.Series(data[data['season']==season_latest]['name'].unique()).to_json(date_format='iso', orient='split')
players_2020_unique_ids_json = pd.Series(data[data['season']==season_latest]['unique_id'].unique()).to_json(date_format='iso', orient='split')

font_size = '10px'
font_size_summary = '20px'
font_size_heading = '40px'

# @cache.memoize(timeout=timeout)

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
@functools.lru_cache()
def render_content(tab):
    if tab == 'PA':
        return (
        #Aggreagate Analysis
        html.Div([

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

            ], style={'width': '48%', 'display': 'inline-block', 'padding-bottom':'5%'}),


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
                            Feature:
                        '''),
                        dcc.Dropdown(
                            id='fig-aggregate-column',
                            options=[{'label': i, 'value': i} for i in available_indicators],
                            value='total_points')
                    ], style={'width': '28%', 'float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            Aggregation type:
                        '''),
                        dcc.Dropdown(
                            id='fig-aggregate-column-type',
                            options=[{'label': i, 'value': i} for i in ['mean', 'median', 'total']],
                            value='mean')
                    ], style={'width': '28%', 'float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            Location:
                        '''),
                        dcc.Dropdown(
                            id='fig-aggregate-column-loc',
                            options=[{'label': i, 'value': i} for i in ['any', 'home', 'away']],
                            value='any')
                    ], style={'width': '28%', 'float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            n:
                        '''),
                        dcc.Dropdown(
                            id='fig-aggregate-column-n',
                            options=[{'label': i, 'value': i} for i in ['3', '4', '5', 'all']],
                            value='4')
                    ], style={'width': '15%', 'float': 'left', 'display': 'inline-block'}),
                ]),

                html.Div([
                        html.Div(children='''
                            No. players to display:
                        '''),

                        dcc.Input(
                            id='n',
                            value='10')
                    ], style={'width': '100%', 'float': 'right', 'display': 'inline-block'}),


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
                    options=[{'label': i, 'value': i} for i in available_indicators_all],
                    value='name_last')
                ], style={'width': '22%', 'display': 'inline-block'}),

            html.Div([
                html.Div(children='''
                    y-data:
                '''),
                dcc.Dropdown(
                    id='fig1-yaxis-column',
                    options=[{'label': i, 'value': i} for i in available_indicators_all],
                    value='mean_total_points_any_4')
                ], style={'width': '22%', 'float': 'center', 'display': 'inline-block'}),

            html.Div([
                html.Div(children='''
                    Error bars:
                '''),
                dcc.Dropdown(
                    id='fig1-errorbar-column',
                    options=[{'label': i, 'value': i} for i in ['std', 'se', 'range']],
                    value='se')
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
        ]),

        #Indiviual Analysis
        html.Div([
            # Column 1 - Player Info
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
                                value=2828,
                                # value=2828,
                                multi=False),
                            style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
                        ]),


                        html.Div([
                            html.Div('''Position: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''FWD ''', id='IPL_position', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Team: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''Leeds Utd. ''', id='IPL_team', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Cost: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''6.5M ''', id='IPL_value', style={'width': '25%', 'display': 'inline-block'}),

                        ]),

                        html.Div([
                            html.Div('''Selected: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_selected', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Fitness to play: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_FTP', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''News: ''', style={'width': '35%', 'display': 'inline-block'}),
                            html.Div('''''', id='IPL_news', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
                        ]),

                    ], style={'width': '70%','float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(id='IPL_player_picture',style={'width': '90%'})

                    ], style={'width': '23%', 'float': 'right', 'display': 'inline-block'})

                ], style={'width': '98%', 'display': 'inline-block'}),


                html.Div(
                        children='''
                        Reference Player Data:
                    ''', style={'font-size': '30px'}),

                html.Div([
                    html.Div([

                        html.Div([
                            html.Div('''Reference Player: ''', style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),
                            html.Div(dcc.Dropdown(
                                id='IPL_reference_player',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                # value=2828,
                                value=3097,
                                multi=False),
                            style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
                        ]),

                        html.Div([
                            html.Div('''Position: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''GKP ''', id='IPL_position_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Team: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''Leeds Utd. ''', id='IPL_team_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Cost: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''6.5M ''', id='IPL_value_reference', style={'width': '25%', 'display': 'inline-block'}),

                        ]),

                        html.Div([
                            html.Div('''Selected: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_selected_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),

                        html.Div([
                            html.Div('''Fitness to play: ''', style={'width': '40%', 'display': 'inline-block'}),
                            html.Div('''47.8% ''', id='IPL_FTP_reference', style={'width': '25%', 'display': 'inline-block'}),
                        ]),


                        html.Div([
                            html.Div('''News (Reference): ''', style={'width': '35%', 'display': 'inline-block'}),
                            html.Div('''''', id='IPL_news_reference', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
                        ]),



                    ], style={'width': '70%','float': 'left', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(id='IPL_reference_player_picture',style={'width': '90%'})

                    ], style={'width': '23%', 'float': 'right', 'display': 'inline-block'})

                ], style={'width': '98%', 'display': 'inline-block'}),

            ], style={'width': '33%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            # # Column 1 - Player Info
            # html.Div([
            #     html.Div(
            #             children='''
            #             Player Data:
            #         ''', style={'font-size': '30px'}),
            #
            #     html.Div([
            #         html.Div([
            #
            #             html.Div([
            #                 html.Div('''Player Name: ''', style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),
            #                 html.Div(dcc.Dropdown(
            #                     id='IPL_playerselect',
            #                     options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
            #                     value=2828,
            #                     # value=2828,
            #                     multi=False),
            #                 style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Reference Player: ''', style={'width': '40%', 'display': 'inline-block', 'float': 'left'}),
            #                 html.Div(dcc.Dropdown(
            #                     id='IPL_reference_player',
            #                     options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
            #                     # value=2828,
            #                     value=3097,
            #                     multi=False),
            #                 style={'width': '55%', 'display': 'inline-block', 'float': 'left'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Position: ''', style={'width': '40%', 'display': 'inline-block'}),
            #                 html.Div('''FWD ''', id='IPL_position', style={'width': '25%', 'display': 'inline-block'}),
            #                 html.Div('''GKP ''', id='IPL_position_reference', style={'width': '25%', 'display': 'inline-block'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Team: ''', style={'width': '40%', 'display': 'inline-block'}),
            #                 html.Div('''Leeds Utd. ''', id='IPL_team', style={'width': '25%', 'display': 'inline-block'}),
            #                 html.Div('''Leeds Utd. ''', id='IPL_team_reference', style={'width': '25%', 'display': 'inline-block'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Cost: ''', style={'width': '40%', 'display': 'inline-block'}),
            #                 html.Div('''6.5M ''', id='IPL_value', style={'width': '25%', 'display': 'inline-block'}),
            #                 html.Div('''6.5M ''', id='IPL_value_reference', style={'width': '25%', 'display': 'inline-block'}),
            #
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Selected: ''', style={'width': '40%', 'display': 'inline-block'}),
            #                 html.Div('''47.8% ''', id='IPL_selected', style={'width': '25%', 'display': 'inline-block'}),
            #                 html.Div('''47.8% ''', id='IPL_selected_reference', style={'width': '25%', 'display': 'inline-block'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''Fitness to play: ''', style={'width': '40%', 'display': 'inline-block'}),
            #                 html.Div('''47.8% ''', id='IPL_FTP', style={'width': '25%', 'display': 'inline-block'}),
            #                 html.Div('''47.8% ''', id='IPL_FTP_reference', style={'width': '25%', 'display': 'inline-block'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''News: ''', style={'width': '35%', 'display': 'inline-block'}),
            #                 html.Div('''''', id='IPL_news', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
            #             ]),
            #
            #             html.Div([
            #                 html.Div('''News (Reference): ''', style={'width': '35%', 'display': 'inline-block'}),
            #                 html.Div('''''', id='IPL_news_reference', style={'width': '60%', 'float': 'right', 'display': 'inline-block'}),
            #             ]),
            #
            #
            #
            #         ], style={'width': '70%','float': 'left', 'display': 'inline-block'}),
            #
            #         html.Div([
            #             html.Div(id='IPL_player_picture',style={'width': '90%'})
            #
            #         ], style={'width': '23%', 'float': 'right', 'display': 'inline-block'})
            #
            #     ], style={'width': '98%', 'display': 'inline-block'}),
            #
            # ], style={'width': '33%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),



            # Column 2
            html.Div([

                # Indicators Row 1
                html.Div([

                    html.Div([
                    # Player Form
                        html.Div(
                                children='''
                                Player Form
                            ''', style={'font-size': '20px', 'text-align': 'center', 'text-decoration': 'underline'}),

                        # Form
                        html.Div(
                            dcc.Graph(id='IPA_indicator_form'), style={'width': '90%', 'display': 'inline-block', 'padding': '5%'}
                        )

                    ], style={'width': '48%', 'display': 'inline-block', 'padding': '1%'}),

                    html.Div([
                        # Total points
                        html.Div(
                                children='''
                                Total Points
                            ''', style={'font-size': '20px', 'text-align': 'center', 'text-decoration': 'underline'}),

                        html.Div(
                            dcc.Graph(id='IPA_indicator_totalpoints'), style={'width': '90%', 'display': 'inline-block', 'padding': '5%'}

                        )
                    ], style={'width': '48%', 'display': 'inline-block', 'padding': '1%'}),

                ],style={'width': '100%', 'display': 'inline-block'}),


                # Initcators row 2
                html.Div([

                    html.Div([
                    # ICT Index
                        html.Div(
                                children='''
                                ICT Index
                            ''', style={'font-size': '20px', 'text-align': 'center', 'text-decoration': 'underline'}),

                        # Form
                        html.Div(
                            dcc.Graph(id='IPA_indicator_ICT'), style={'width': '90%', 'display': 'inline-block', 'padding': '5%'}
                        )

                    ], style={'width': '48%', 'float': 'left', 'display': 'inline-block', 'padding': '1%'}),

                    html.Div([
                    # Probabilities
                        html.Div(
                                children='''
                                Probabilities
                            ''', style={'font-size': '20px', 'text-align': 'center', 'text-decoration': 'underline'}),

                        html.Div(
                            dcc.Graph(id='IPA_indicator_prob'), style={'width': '90%', 'display': 'inline-block', 'padding': '5%'}

                        )
                    ], style={'width': '48%', 'float': 'left', 'display': 'inline-block', 'padding': '1%'}),

                ],style={'width': '100%', 'display': 'inline-block'}),


                # Histogram
                html.Div(
                        children='''
                        Histogram of total points:
                    ''', style={'font-size': '20px'}),

                html.Div([
                    dcc.Graph(id='IPL_histogram'),

                ], style={'padding-bottom': '3%'}),


                ],style={'width': '62%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid", 'padding': '1%'}),
            ])
        )
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
                        dcc.Graph(id='LA-fig-league_graph'),

                    html.Div([
                        html.Div(children='''
                            x-data:
                        '''),

                        dcc.Dropdown(
                            id='LA-fig1-xaxis-column',
                            options=[{'label': i, 'value': i} for i in labels_league_standings],
                            value='round')
                        ], style={'width': '48%', 'float': 'center', 'display': 'inline-block'}),

                    html.Div([
                        html.Div(children='''
                            y-data:
                        '''),
                        dcc.Dropdown(
                            id='LA-fig1-yaxis-column',
                            options=[{'label': i, 'value': i} for i in labels_league_standings],
                            value='total_points')
                        ], style={'width': '48%', 'float': 'center', 'display': 'inline-block'}),

                    ]),
                ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            ]),

        ])
        )

######################################################################################################################
################################################ Callbacks ###########################################################
######################################################################################################################

@app.callback(
    [Output('IPA_indicator_form', 'figure'),
     Output('IPA_indicator_totalpoints', 'figure'),
     Output('IPA_indicator_ICT', 'figure'),
     Output('IPA_indicator_prob', 'figure'),
     Output('IPL_histogram', 'figure'),
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
     Output('IPL_news_reference', 'children'),
     Output('IPL_reference_player_picture', 'children')],
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
    element_photo_reference = element_data[element_data['id']==element_id_reference]['photo'].values[0][:-4]
    element_photo_reference += '.png'

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
        height = 200,
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
        height = 200,
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

    ICT = data_IPL_player[data_IPL_player['round']==round_max]['mean_ict_index_any_all'].values[0]
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
        height = 170,
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
        height = 170,
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


    player_img = html.Img(src='https://resources.premierleague.com/premierleague/photos/players/110x140/p' + element_photo,style={'width': '90%'})
    player_img_reference = html.Img(src='https://resources.premierleague.com/premierleague/photos/players/110x140/p' + element_photo_reference,style={'width': '90%'})

    return indicator_form, indicator_totalpoints, indicator_ICT, indicator_prob, points_histogram, \
           element_position, element_team, element_value, element_selected, element_FTP, element_news, player_img, \
           element_position_reference, element_team_reference, element_value_reference, element_selected_reference, element_FTP_reference, element_news_reference, player_img_reference

@app.callback(
    [Output('LA-fig-league_graph', 'figure'),
     Output('table_league', 'data')],
    [Input('input-league_id','value')],
    [State('LA-fig1-xaxis-column','value'),
     State('LA-fig1-yaxis-column','value')])
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
    Output('LA-fig-league_graph', 'figure'),
    [Input('LA-fig1-xaxis-column','value'),
     Input('LA-fig1-yaxis-column','value')])
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
     Input('fig-aggregate-column-type', 'value'),
     Input('fig-aggregate-column-loc', 'value'),
     Input('fig-aggregate-column-n', 'value'),
     Input('fig1-errorbar-column', 'value'),
     Input('year-filter', 'value'),
     Input('player-filter', 'value'),
     Input('position-type', 'value'),
     Input('player-selection-type', 'value'),
     Input('n', 'value')])
def APA_update_aggregate_graph(plot_type,
                        xaxis_column_name,
                        yaxis_column_name,
                        aggregate_column_target,
                        aggregate_column_type,
                        aggregate_column_location,
                        aggregate_column_n,
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

    aggregate_column_name = aggregate_column_type + '_' + aggregate_column_target + '_' + aggregate_column_location + '_' + aggregate_column_n

    data_filt = data.copy()
    data_filt = data_filt[data_filt['season']==season]

    element_type = postion2element_type(position_type)

    y_data_error = determine_error_bar(aggregate_column_target, aggregate_column_type, aggregate_column_location, aggregate_column_n, errorbar_column_name)

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
            # data_filt = data_filt.groupby('unique_id').mean()
            # data_filt.reset_index(level=0, inplace=True)


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
                     y=aggregate_column_target,
                     points="all")

        fig.update_traces(customdata=data_filt['unique_id'].unique(), selector=dict(type='box'))

        fig.update(layout_coloraxis_showscale=False)

        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest', yaxis_title=aggregate_column_target,)
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


def determine_error_bar(aggregate_column_target, aggregate_column_type, aggregate_column_location, aggregate_column_n,  error_bar_type):

    y_data_error = error_bar_type + '_' + aggregate_column_target + '_' + aggregate_column_location + '_' + aggregate_column_n

    return y_data_error



@app.callback(
    [Output('fig1-yaxis-column', 'value')],
    [Input('fig-aggregate-column', 'value'),
     Input('fig-aggregate-column-type', 'value'),
     Input('fig-aggregate-column-loc', 'value'),
     Input('fig-aggregate-column-n', 'value')],
    [State('fig1-yaxis-column', 'value')])
def update_aggregate_figure_ycol(aggregate_column_target,
                                aggregate_column_type,
                                aggregate_column_location,
                                aggregate_column_n,
                                fig1_yaxis_column):

    fig_aggregate_column = aggregate_column_type + '_' + aggregate_column_target + '_' + aggregate_column_location + '_' + aggregate_column_n

    if fig_aggregate_column is not None:
        return [fig_aggregate_column]
    else:
        return [fig1_yaxis_column]


# @app.callback(
#     Output('fig1-aggregate-graph', 'fig'),
#     [Input('fig1-yaxis-column', 'value'),
#      Input('fig1-errorbar-column', 'value')],
#     [State('fig1-aggregate-graph', 'fig')])
# def update_aggregate_figure_ycol_error(fig_yaxis_column,
#                                         fig1_errorbar_column,
#                                         fig):
#
#     y_data_error = determine_error_bar(fig_yaxis_column, fig1_errorbar_column)
#     if fig is not None:
#         fig.update(error_y=y_data_error)
#     return fig


# if __name__ == '__main__':
#     app.run_server(debug=False, host='192.168.0.36', port=8051)

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
