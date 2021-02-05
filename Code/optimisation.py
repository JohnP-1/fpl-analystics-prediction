import cvxpy
import numpy as np
import pandas as pd
import os.path as path
import DataLoader as DL


def determine_element_id(data, unique_id, season):

    return data[(data['season']==season) & (data['unique_id']==unique_id)]['element'].unique()[0]

def determine_unique_id(data, element_id, season):

    return int(data[(data['season']==season) & (data['element']==element_id)]['unique_id'].unique()[0])


def get_chance_of_playing(data, data_raw, player_unique_id, season):

    player_id = determine_element_id(data, player_unique_id, season)

    for i in range(data.shape[0]):
        if data_raw['id'].iloc[i] == player_id:
            chance_of_playing = data_raw['chance_of_playing_this_round'].iloc[i]
            if np.isnan(chance_of_playing) == True:
                chance_of_playing = 100
            return chance_of_playing


pd.set_option('display.max_columns', None)

# Import the data:
path_processed = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed')
path_modelling = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Prediction')

filename_player_database = 'player_database.csv'
filename_selection = 'team_selection.csv'

player_data = pd.read_csv(path.join(path_processed, filename_player_database))

DataLoaderObj = DL.DataLoader()
data_raw = DataLoaderObj.scrape_bootstrap_static(keys=['elements'])['elements']

season = 2020

player_data = player_data[player_data['season']==season]
unique_ids = player_data['unique_id'].unique()

player_temp_list = []

for unique_id in unique_ids:
    cop = get_chance_of_playing(player_data, data_raw, unique_id, season)
    data_temp = player_data[player_data['unique_id']==unique_id]
    data_temp = data_temp[data_temp['round']==data_temp['round'].max()]
    data_temp['cop'] = cop
    if cop >= 75:
        player_temp_list.append(data_temp)

player_data = pd.concat(player_temp_list, axis=0).reset_index(drop=True)


pred_column = 'mean_total_points_any_10'

player_data = player_data.dropna(subset=[pred_column])

print(player_data[pred_column])

player_ids = player_data['unique_id'].values
player_costs = player_data['value'].values/10
player_teams = pd.get_dummies(player_data['team_id']).values
player_positions = pd.get_dummies(player_data['element_type']).values
player_points_preds = player_data[pred_column].values

# The first task is to optimise the squad which is done through optimising the maximum expected points for all 15 players

# This defines the limits which will then be used to construct the optimisation constraints
team_cost_max = 97.8
max_players_team = 3
max_selections = 15
max_element_type_1 = 2
max_element_type_2 = 5
max_element_type_3 = 5
max_element_type_4 = 3

# The selection is a boolean variable which defines the selected players
selection = cvxpy.Variable(len(player_costs), boolean=True)

# Constraint to make the total cost less than the available money
cost_constraint = player_costs @ selection <= team_cost_max

# Constrain the optimisation to make sure 15 players a picked
total_player_constraint = cvxpy.sum(selection) == max_selections

# Constrain the optimisation to make sure the correct number of players are selected for each position
element_type_1_constraint = player_positions[:, 0] @ selection == max_element_type_1
element_type_2_constraint = player_positions[:, 1] @ selection == max_element_type_2
element_type_3_constraint = player_positions[:, 2] @ selection == max_element_type_3
element_type_4_constraint = player_positions[:, 3] @ selection == max_element_type_4

# Constrain the optimisation to make sure no more than three players per team are selected
team_1_constraint = player_teams[:, 0] @ selection <= max_players_team
team_2_constraint = player_teams[:, 1] @ selection <= max_players_team
team_3_constraint = player_teams[:, 2] @ selection <= max_players_team
team_4_constraint = player_teams[:, 3] @ selection <= max_players_team
team_5_constraint = player_teams[:, 4] @ selection <= max_players_team
team_6_constraint = player_teams[:, 5] @ selection <= max_players_team
team_7_constraint = player_teams[:, 6] @ selection <= max_players_team
team_8_constraint = player_teams[:, 7] @ selection <= max_players_team
team_9_constraint = player_teams[:, 8] @ selection <= max_players_team
team_10_constraint = player_teams[:, 9] @ selection <= max_players_team
team_11_constraint = player_teams[:, 10] @ selection <= max_players_team
team_12_constraint = player_teams[:, 11] @ selection <= max_players_team
team_13_constraint = player_teams[:, 12] @ selection <= max_players_team
team_14_constraint = player_teams[:, 13] @ selection <= max_players_team
team_15_constraint = player_teams[:, 14] @ selection <= max_players_team
team_16_constraint = player_teams[:, 15] @ selection <= max_players_team
team_17_constraint = player_teams[:, 16] @ selection <= max_players_team
team_18_constraint = player_teams[:, 17] @ selection <= max_players_team
team_19_constraint = player_teams[:, 18] @ selection <= max_players_team
team_20_constraint = player_teams[:, 19] @ selection <= max_players_team

# Define the optimisation problem
total_points = player_points_preds @ selection

optimisation_problem = cvxpy.Problem(cvxpy.Maximize(total_points), [cost_constraint,
                                                                    total_player_constraint,
                                                                    element_type_1_constraint,
                                                                    element_type_2_constraint,
                                                                    element_type_3_constraint,
                                                                    element_type_4_constraint,
                                                                    team_1_constraint,
                                                                    team_2_constraint,
                                                                    team_3_constraint,
                                                                    team_4_constraint,
                                                                    team_5_constraint,
                                                                    team_6_constraint,
                                                                    team_7_constraint,
                                                                    team_8_constraint,
                                                                    team_9_constraint,
                                                                    team_10_constraint,
                                                                    team_11_constraint,
                                                                    team_12_constraint,
                                                                    team_13_constraint,
                                                                    team_14_constraint,
                                                                    team_15_constraint,
                                                                    team_16_constraint,
                                                                    team_17_constraint,
                                                                    team_18_constraint,
                                                                    team_19_constraint,
                                                                    team_20_constraint])

# Solving the problem
optimisation_problem.solve(solver=cvxpy.GLPK_MI)

selection = selection.value

columns = ['name', 'team_name', 'element_type', pred_column]

print('The total team cost = ', selection @ player_costs)
print('The team expected points = ', player_data[pred_column].iloc[selection.nonzero()].sum())
print(player_data[columns].iloc[selection.nonzero()])

final_selection = player_data[columns].iloc[selection.nonzero()]
# final_selection['selected'] = 0

#The next step is to select the best team based on the squad, this is once again done through mixed integer optimisation

player_data_filt = player_data.iloc[selection.nonzero()]

player_positions_selected = pd.get_dummies(player_data_filt['element_type']).values
player_points_preds_selected = player_data_filt[pred_column].values


# This defines the limits which will then be used to construct the optimisation constraints
max_selections = 11
max_element_type_1 = 1
max_element_type_2 = 5
max_element_type_3 = 5
max_element_type_4 = 3
min_element_type_2 = 3
min_element_type_3 = 3
min_element_type_4 = 1

# The selection is a boolean variable which defines the selected players
selection = cvxpy.Variable(len(player_positions_selected), boolean=True)

# # Constraint to make the total cost less than the available money
# cost_constraint = player_costs @ selection <= team_cost_max

# Constrain the optimisation to make sure 15 players a picked
total_player_constraint = cvxpy.sum(selection) == max_selections

# Constrain the optimisation to make sure the correct number of players are selected for each position
element_type_1_constraint = player_positions_selected[:, 0] @ selection == max_element_type_1

element_type_2_constraint_max = player_positions_selected[:, 1] @ selection <= max_element_type_2
element_type_3_constraint_max = player_positions_selected[:, 2] @ selection <= max_element_type_3
element_type_4_constraint_max = player_positions_selected[:, 3] @ selection <= max_element_type_4

element_type_2_constraint_min = player_positions_selected[:, 1] @ selection >= min_element_type_2
element_type_3_constraint_min = player_positions_selected[:, 2] @ selection >= min_element_type_3
element_type_4_constraint_min = player_positions_selected[:, 3] @ selection >= min_element_type_4


# Define the optimisation problem
total_points = player_points_preds_selected @ selection

optimisation_problem = cvxpy.Problem(cvxpy.Maximize(total_points), [total_player_constraint,
                                                                    element_type_1_constraint,
                                                                    element_type_2_constraint_min,
                                                                    element_type_3_constraint_min,
                                                                    element_type_4_constraint_min,
                                                                    element_type_2_constraint_max,
                                                                    element_type_3_constraint_max,
                                                                    element_type_4_constraint_max,
                                                                    ])

# Solving the problem
optimisation_problem.solve(solver=cvxpy.GLPK_MI)

selection = selection.value
#
# print('The total team cost = ', selection @ player_costs)
print('The team expected points = ', player_data_filt[pred_column].iloc[selection.nonzero()].sum())
print(player_data_filt[columns].iloc[selection.nonzero()])

final_selection['selection'] = selection * -1

final_selection = final_selection.sort_values(by=['selection', 'element_type'])

final_selection['selection'] = final_selection['selection'] * -1

final_selection.to_csv(path.join(path_modelling, filename_selection), index=False)
