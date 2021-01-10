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
#      Output('player_1_15_2_player_form', 'children')],
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
#      State('intermediate-team_unique_ids_gw2', 'children'),]
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
#     # #GW + 2
#     # player_2_1_value = player_1_1_unique_id
#     # team_names_2.iloc[0] = player_1_1_player_name
#     # team_unique_ids_2.iloc[0] = player_1_1_unique_id
#     # player_2_1_option = [[{'label': name, 'value': team_unique_ids_1[i]} for i, name in enumerate(team_names_2)]]
#     #
#     # team_names_2_json = team_names_2.to_json(date_format='iso', orient='split')
#     # team_unique_ids_2_json = team_unique_ids_2.to_json(date_format='iso', orient='split')
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
#             player_1_15_value, player_1_15_position, player_1_15_team_code, player_1_15_opposition[0], player_1_15_was_home[0], player_1_15_odds_win[0], player_1_15_player_form[0], player_1_15_opposition[1], player_1_15_was_home[1], player_1_15_odds_win[1], player_1_15_player_form[1])
#             # player_2_1_option, player_2_1_value, team_names_2_json, team_unique_ids_2_json)
