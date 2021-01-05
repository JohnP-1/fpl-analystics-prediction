import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from preprocess import preprocess
import os.path as path
from sklearn.decomposition import PCA

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'model_database.csv')
data = pd.read_csv(path_data)

seed = 1000
seed_test = 100

data_preprocesser = preprocess()

data = data[data['season']!=2020]
data = data[data['minutes']!=0]

data = data_preprocesser.shuffle_dataset(data, seed=seed_test)
data, data_test = data_preprocesser.split_dataset(data, split=0.8)
data_train, data_val = data_preprocesser.split_dataset(data, split=0.7)

unique_id_column = 'unique_id'

# feature_columns = ['assists',
#                    'bonus',
#                    'bps',
#                    'clean_sheets',
#                    'creativity',
#                    'element_type_1',
#                    'element_type_2',
#                    'element_type_3',
#                    'element_type_4',
#                    'goals_conceded',
#                    'goals_scored',
#                    'ict_index',
#                    'influence',
#                    'minutes',
#                    'own_goals',
#                    'penalties_missed',
#                    'penalties_saved',
#                    'red_cards',
#                    'round',
#                    'saves',
#                    'selected',
#                    'team_a_score',
#                    'team_h_score',
#                    'threat',
#                    'total_points',
#                    'transfers_balance',
#                    'transfers_in',
#                    'transfers_out',
#                    'value',
#                    'yellow_cards',
#                    'position',
#                    'team_points',
#                    'team_wins',
#                    'team_draws',
#                    'team_losses',
#                    'team_goals_for',
#                    'team_goals_against',
#                    'team_goals_diff',
#                    'team_yc',
#                    'team_rc',
#                    'team_position',
#                    'future_fixture_team_next',
#                    'future_fixture_position_next',
#                    'future_fixture_points_next',
#                    'future_fixture_wins_next',
#                    'future_fixture_draws_next',
#                    'future_fixture_losses_next',
#                    'future_fixture_goals_for_next',
#                    'future_fixture_goals_against_next',
#                    'future_fixture_goals_diff_next',
#                    'future_fixture_played_next',
#                    'future_fixture_yc_next',
#                    'future_fixture_rc_next',
#                    'future_fixture_team_unique_id_next_0',
#                    'future_fixture_team_unique_id_next_1',
#                    'future_fixture_team_unique_id_next_2',
#                    'future_fixture_team_unique_id_next_3',
#                    'future_fixture_team_unique_id_next_4',
#                    'future_fixture_team_unique_id_next_5',
#                    'future_fixture_team_unique_id_next_6',
#                    'future_fixture_team_unique_id_next_7',
#                    'future_fixture_team_unique_id_next_8',
#                    'future_fixture_team_unique_id_next_9',
#                    'future_fixture_team_unique_id_next_10',
#                    'future_fixture_team_unique_id_next_11',
#                    'future_fixture_team_unique_id_next_12',
#                    'future_fixture_team_unique_id_next_13',
#                    'future_fixture_team_unique_id_next_14',
#                    'future_fixture_team_unique_id_next_15',
#                    'future_fixture_team_unique_id_next_16',
#                    'future_fixture_team_unique_id_next_17',
#                    'future_fixture_team_unique_id_next_18',
#                    'future_fixture_team_unique_id_next_19',
#                    'future_fixture_team_unique_id_next_20',
#                    'future_fixture_team_unique_id_next_21',
#                    'future_fixture_team_unique_id_next_22',
#                    'future_fixture_team_unique_id_next_23',
#                    'future_fixture_team_unique_id_next_24',
#                    'future_fixture_team_unique_id_next_25',
#                    'future_fixture_team_unique_id_next_26',
#                    'future_fixture_team_unique_id_next_27',
#                    'future_fixture_team_unique_id_next_28',
#                    'future_fixture_team_unique_id_next_29',
#                    'future_fixture_team_unique_id_next_30']

# feature_columns = ['points_next',
#                    'assists',
#                    'bonus',
#                    'bps',
#                    'creativity',
#                    'goals_scored',
#                    'ict_index',
#                    'influence',
#                    'penalties_missed',
#                    'selected',
#                    'team_a_score',
#                    'team_h_score',
#                    'threat',
#                    'total_points',
#                    'value',
#                    'team_points',
#                    'team_wins',
#                    'team_draws',
#                    'team_losses',
#                    'team_goals_for',
#                    'team_goals_against',
#                    'team_goals_diff',
#                    'team_position']

# feature_columns = ['points_next',
#                    'assists',
#                    'bonus',
#                    'bps',
#                    'creativity',
#                    'goals_scored',
#                    'ict_index',
#                    'influence',
#                    'threat',
#                    'total_points',
#                    'value']

# feature_columns = ['points_next',
#                    'assists_median',
#                    'bonus_median',
#                    'bps_median',
#                    'clean_sheets_median',
#                    'creativity_median',
#                    'goals_conceded_median',
#                    'goals_scored_median',
#                    'ict_index_median',
#                    'influence_median',
#                    'minutes_median',
#                    'own_goals_median',
#                    'penalties_missed_median',
#                    'red_cards_median',
#                    'saves_median',
#                    'threat_median',
#                    'yellow_cards_median',
#                    'points_median']

# feature_columns = ['points_next',
#                    'assists_mean',
#                    'bonus_mean',
#                    'bps_mean',
#                    'clean_sheets_mean',
#                    'creativity_mean',
#                    'goals_conceded_mean',
#                    'goals_scored_mean',
#                    'ict_index_mean',
#                    'influence_mean',
#                    'minutes_mean',
#                    'own_goals_mean',
#                    'penalties_missed_mean',
#                    'red_cards_mean',
#                    'saves_mean',
#                    'threat_mean',
#                    'yellow_cards_mean',
#                    'points_mean']

feature_columns = ['assists_mean3',
                   'bonus_mean3',
                   'bps_mean3',
                   'clean_sheets_mean3',
                   'creativity_mean3',
                   'goals_conceded_mean3',
                   'goals_scored_mean3',
                   'ict_index_mean3',
                   'influence_mean3',
                   'own_goals_mean3',
                   'red_cards_mean3',
                   'saves_mean3',
                   'threat_mean3',
                   'yellow_cards_mean3',
                   'points_mean3']


response_columns = ['points_next']

X_train = data_train[feature_columns].values
yy_train = data_train[response_columns].values
unique_id_train = data_train[unique_id_column]

X_val = data_val[feature_columns].values
yy_val = data_val[response_columns].values
unique_id_val = data_val[unique_id_column]

X_test = data_test[feature_columns].values
yy_test = data_test[response_columns].values
unique_id_test = data_test[unique_id_column]

data_1 = data[data['element_type_1'] == 1]
data_2 = data[data['element_type_2'] == 1]
data_3 = data[data['element_type_3'] == 1]
data_4 = data[data['element_type_4'] == 1]

# sns.displot(data_1, x="points_next")
# sns.displot(data_2, x="points_next")
# sns.displot(data_3, x="points_next")
# sns.displot(data_4, x="points_next")
# sns.pairplot(data_2[feature_columns])
# plt.show()

X_train, scaler = data_preprocesser.scale_features(data_4[feature_columns])
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

score_columns = []
for i in range(X_train.shape[1]):
    score_columns.append('PC' + str(i))

pca = PCA().fit(X_train)
pc_scores = pca.transform(X_train)
pc_scores = pd.DataFrame(pc_scores, columns=score_columns)
pc_scores = pd.concat([pc_scores.reset_index(), data_train.reset_index()['points_next']], axis=1)

sns.scatterplot(data=pc_scores, x='PC1', y='PC2', hue='points_next')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.grid()
plt.show()

sns.scatterplot(data=pc_scores, x='PC3', y='PC4', hue='points_next')
plt.xlabel('PC3')
plt.ylabel('PC4')
plt.grid()
plt.show()

