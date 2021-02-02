import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import os.path as path
import json


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
    """

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


########### Global Variables #################

# unique_ids_clickData = []

##############################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_database.csv')

data = pd.read_csv(path_data)

data['points_mean3/pound'] = data['points_mean3'] / (data['value'] / 10)
data['points_mean5/pound'] = data['points_mean5'] / (data['value'] / 10)
data['points_total/pound'] = data['points_total'] / (data['value'] / 10)
data['name_first'] = data['name'].str.split('_', expand=True)[0]
data['name_last'] = data['name'].str.split('_', expand=True)[1].str.slice(start=0, stop=20)


available_indicators = data.columns

app.layout = html.Div([
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
                    options=[{'label': i, 'value': i} for i in data.sort_values(by='name_last')[data['season']==2020]['name'].unique()],
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
                        value='points_mean3')
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
                value='points_mean3')
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
    ]),
])

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
                     color="points_mean_grad3",
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
        data_filt = data_filt[(data_filt['season']==2020)]
        return [{'label': i, 'value': i} for i in data_filt.sort_values(by='name_last')[(data_filt['element_type']==element_type)]['name'].unique()], unique_id_clickData.to_json(date_format='iso', orient='split')
    else:
        return [{'label': i, 'value': i} for i in data.sort_values(by='name_last')[data['season']==2020]['name'].unique()], unique_id_clickData.to_json(date_format='iso', orient='split')


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


    unique_id_clickData = pd.read_json(unique_ids_clickData_json, orient='split', typ='series')

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

    y_data_split = y_data.split('_')[:-1]
    y_data_type = y_data.split('_')[-1]

    if error_bar_type == 'Standard Deviation':
        error_bar_type = 'std'
    elif error_bar_type == 'Standard Error':
        error_bar_type = 'se'


    if y_data_type == 'mean':
        y_data_error = ''
        for item in y_data_split:
            y_data_error = y_data_error + item + '_'
        y_data_error = y_data_error + error_bar_type
    elif y_data_type[:-1] == 'mean':
        y_data_error = ''
        for item in y_data_split:
            y_data_error = y_data_error + item + '_'
        y_data_error = y_data_error + error_bar_type + y_data_type[-1]
    else:
        y_data_error = 'points_se3'

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
