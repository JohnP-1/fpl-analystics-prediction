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

    return data[(data['unique_id']==unique_id) & (data['round']==max_round)]['team_unique_id'].values

def determine_player_position(data, unique_id):

    element_type = data[data['unique_id']==unique_id]['element_type'].unique()[0]

    return element_type2position(element_type)


def planner_process_player(data, element_id, season):
    unique_id = determine_unique_id(data, element_id, season)
    player_form = '{0:.2f}'.format(determine_player_form(data, unique_id))
    team_unique_id = determine_player_team_unique_id(data, unique_id)
    player_position = determine_player_position(data, unique_id)

    return unique_id, player_form, team_unique_id, player_position

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

data = pd.read_csv(path_data)
player_metadata = pd.read_csv(path_player_metadata)
team_metadata = pd.read_csv(path_team_metadata)

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


player_names = []
unique_ids = []

for i in range(player_metadata_season.shape[0]):
    player_name_key = player_metadata_season['name'].iloc[i]
    player_name = player_metadata_season['name_first'].iloc[i] + ' ' + player_metadata_season['name_last'].iloc[i]
    unique_id = player_metadata_season['unique_id'].iloc[i]
    player_names.append(player_name)
    unique_ids.append(unique_id)

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

        fixtures = pd.read_csv('/home/john/Documents/projects/fpl-analystics-prediction/Data/2020-21/fixtures.csv')

        font_size = '10px'

        player_1_id = team_picks['element'].iloc[0]
        player_1_captain = team_picks['is_captain'].iloc[0]
        player_1_unique_id, player_1_player_form, player_1_team_unique_id, player_1_position = planner_process_player(data, player_1_id, season_latest)

        # player_1_unique_id = determine_unique_id(data, player_1_id, season_latest)
        # player_1_player_form = '{0:.2f}'.format(determine_player_form(data, player_1_unique_id))
        # player_1_team_unique_id = determine_player_team_unique_id(data, player_1_unique_id)
        # player_1_player_position = determine_player_position(data, player_1_unique_id)

        player_2_id = team_picks['element'].iloc[1]
        player_2_captain = team_picks['is_captain'].iloc[1]
        player_2_unique_id, player_2_player_form, player_2_team_unique_id, player_2_position = planner_process_player(data, player_2_id, season_latest)


        player_3_id = team_picks['element'].iloc[2]
        player_3_captain = team_picks['is_captain'].iloc[2]
        player_3_unique_id, player_3_player_form, player_3_team_unique_id, player_3_position = planner_process_player(data, player_3_id, season_latest)

        player_4_id = team_picks['element'].iloc[3]
        player_4_captain = team_picks['is_captain'].iloc[3]
        player_4_unique_id, player_4_player_form, player_4_team_unique_id, player_4_position = planner_process_player(data, player_4_id, season_latest)

        player_5_id = team_picks['element'].iloc[4]
        player_5_captain = team_picks['is_captain'].iloc[4]
        player_5_unique_id, player_5_player_form, player_5_team_unique_id, player_5_position = planner_process_player(data, player_5_id, season_latest)

        player_6_id = team_picks['element'].iloc[5]
        player_6_captain = team_picks['is_captain'].iloc[5]
        player_6_unique_id, player_6_player_form, player_6_team_unique_id, player_6_position = planner_process_player(data, player_6_id, season_latest)


        player_7_id = team_picks['element'].iloc[6]
        player_7_captain = team_picks['is_captain'].iloc[6]
        player_7_unique_id, player_7_player_form, player_7_team_unique_id, player_7_position = planner_process_player(data, player_7_id, season_latest)


        player_8_id = team_picks['element'].iloc[7]
        player_8_captain = team_picks['is_captain'].iloc[7]
        player_8_unique_id, player_8_player_form, player_8_team_unique_id, player_8_position = planner_process_player(data, player_8_id, season_latest)


        player_9_id = team_picks['element'].iloc[8]
        player_9_captain = team_picks['is_captain'].iloc[8]
        player_9_unique_id, player_9_player_form, player_9_team_unique_id, player_9_position = planner_process_player(data, player_9_id, season_latest)


        player_10_id = team_picks['element'].iloc[9]
        player_10_captain = team_picks['is_captain'].iloc[9]
        player_10_unique_id, player_10_player_form, player_10_team_unique_id, player_10_position = planner_process_player(data, player_10_id, season_latest)


        player_11_id = team_picks['element'].iloc[10]
        player_11_captain = team_picks['is_captain'].iloc[10]
        player_11_unique_id, player_11_player_form, player_11_team_unique_id, player_11_position = planner_process_player(data, player_11_id, season_latest)

        player_s1_id = team_picks['element'].iloc[11]
        player_s1_captain = team_picks['is_captain'].iloc[11]
        player_s1_unique_id, player_s1_player_form, player_s1_team_unique_id, player_s1_position = planner_process_player(data, player_s1_id, season_latest)

        player_s2_id = team_picks['element'].iloc[12]
        player_s2_captain = team_picks['is_captain'].iloc[12]
        player_s2_unique_id, player_s2_player_form, player_s2_team_unique_id, player_s2_position = planner_process_player(data, player_s2_id, season_latest)

        player_s3_id = team_picks['element'].iloc[13]
        player_s3_captain = team_picks['is_captain'].iloc[13]
        player_s3_unique_id, player_s3_player_form, player_s3_team_unique_id, player_s3_position = planner_process_player(data, player_s3_id, season_latest)

        player_s4_id = team_picks['element'].iloc[14]
        player_s4_captain = team_picks['is_captain'].iloc[14]
        player_s4_unique_id, player_s4_player_form, player_s4_team_unique_id, player_s4_position = planner_process_player(data, player_s4_id, season_latest)


        return (
            html.Div([html.Div([
                html.Div(children='GW+1'),

                html.Div([
                    html.Div(children='No.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Pos', id='pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Name', id='name', style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team', id='team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Agst.', id='Agst.', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Home/ Away', id='H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Player Form', id='player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Team Form', id='team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Odds (win)', id='team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Cpt.', id='captain', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),
                    html.Div(children='Trn.', id='transfer', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center', 'font-weight': 'bold'}),

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='1.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_1_position, id='player_1_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_1_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_1_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_1_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_1_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_1_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_1_player_form, id='player_1_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_1_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_1_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_1_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_1_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                    # html.Div(children='1242', id='player_1_team_ICT', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': '8px', 'text-align': 'center'}),

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='2.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_2_position, id='player_2_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_2_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_2_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_2_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_2_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_2_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_2_player_form, id='player_2_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_2_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_2_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_2_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_2_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='3.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_3_position, id='player_3_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_3_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_3_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_3_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_3_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_3_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_3_player_form, id='player_3_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_3_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_3_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_3_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_3_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='4.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_4_position, id='player_4_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_4_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_4_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_4_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_4_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_4_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_4_player_form, id='player_4_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_4_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_4_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_4_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_4_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='5.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': '8px', 'text-align': 'center'}),
                    html.Div(children=player_5_position, id='player_5_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_5_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_5_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_5_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_5_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_5_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_5_player_form, id='player_5_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_5_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_5_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_5_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_5_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='6.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_6_position, id='player_6_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_6_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_6_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_6_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_6_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_6_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_6_player_form, id='player_6_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_6_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_6_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_6_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_6_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='7.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_7_position, id='player_7_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_7_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_7_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_7_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_7_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_7_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_7_player_form, id='player_7_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_7_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_7_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_7_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_7_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='8.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_8_position, id='player_8_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_8_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_8_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_8_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_8_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_8_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_8_player_form, id='player_8_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_8_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_8_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_8_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_8_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='9.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_9_position, id='player_9_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_9_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_9_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_9_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_9_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_9_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_9_player_form, id='player_9_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_9_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_9_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_9_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_9_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='10.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_10_position, id='player_10_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_10_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_10_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_10_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_10_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_10_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_10_player_form, id='player_10_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_10_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_10_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_10_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_10_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='11.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_11_position, id='player_11_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_11_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_11_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_11_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_11_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_11_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_11_player_form, id='player_11_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_11_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_11_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_11_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_11_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'})

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='S1.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s1_position, id='player_s1_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_s1_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_s1_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_s1_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_s1_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_s1_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s1_player_form, id='player_s1_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_s1_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_s1_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_s1_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_s1_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='S2.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s2_position, id='player_s2_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_s2_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_s2_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_s2_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_s2_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_s2_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s2_player_form, id='player_s2_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_s2_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_s2_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_s2_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_s2_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='S3.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s4_position, id='player_s3_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_s3_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_s3_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_s3_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_s3_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_s3_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s3_player_form, id='player_s3_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_s3_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_s3_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_s3_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_s3_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),



                ], style={'width': '100%','float': 'left'}),

                html.Div([
                    html.Div(children='S4.', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s4_position, id='player_s4_pos', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(dcc.Dropdown(
                                id='player_s4_name',
                                options=[{'label': name, 'value': unique_ids[i]} for i, name in enumerate(player_names)],
                                value=player_s4_unique_id,
                                multi=False),
                            style={'width': '29%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size}),
                    html.Div(children='CHE', id='player_s4_team', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='ARS', id='player_s4_against', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='H', id='player_s4_H_A', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children=player_s4_player_form, id='player_s4_player_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5.0', id='player_s4_team_form', style={'width': '8%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(children='5/1', id='player_s4_team_odds', style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'CPT'},
                            ],
                        style={'float': 'center'},
                        id='player_s4_cpt')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),

                    html.Div(
                        dcc.Checklist(
                            options=[
                                {'label': '', 'value': 'TRN'},
                            ],
                        style={'float': 'center'},
                        id='player_s4_transfer')
                    , style={'width': '6%', 'display': 'inline-block', 'float': 'left', 'font-size': font_size, 'text-align': 'center'}),



                ], style={'width': '100%','float': 'left'}),

            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+2'),
                html.Div(children='Data'),
            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+3'),
                html.Div(children='Data'),
            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),

            html.Div([html.Div([
                html.Div(children='GW+4'),
                html.Div(children='Data'),
            ])],style={'width': '24.5%', 'float': 'left', 'display': 'inline-block', "border":"2px black solid"}),
            )


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
    print(round_max_overall)
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
