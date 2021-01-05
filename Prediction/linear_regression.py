import pandas as pd
import numpy as np
from preprocess import preprocess
import os.path as path
from models import LinearRegressionModel
import matplotlib.pyplot as plt

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'model_database.csv')
data = pd.read_csv(path_data)

seed = 1000
seed_test = 100

data_preprocesser = preprocess()

# data = data[data['element_type_3'] == 1]
data = data[data['season']!=2020]
data = data[data['minutes']!=0]

data = data_preprocesser.shuffle_dataset(data, seed=seed_test)
data, data_test = data_preprocesser.split_dataset(data, split=0.8)
data_train, data_val = data_preprocesser.split_dataset(data, split=0.7)

unique_id_column = 'unique_id'

feature_columns = ['assists',
                   'bonus',
                   'bps',
                   'clean_sheets',
                   'creativity',
                   'element_type_1',
                   'element_type_2',
                   'element_type_3',
                   'element_type_4',
                   'goals_conceded',
                   'goals_scored',
                   'ict_index',
                   'influence',
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
                   'yellow_cards',
                   'position',
                   'team_points',
                   'team_wins',
                   'team_draws',
                   'team_losses',
                   'team_goals_for',
                   'team_goals_against',
                   'team_goals_diff',
                   'team_yc',
                   'team_rc',
                   'team_position',
                   'future_fixture_team_next',
                   'future_fixture_position_next',
                   'future_fixture_points_next',
                   'future_fixture_wins_next',
                   'future_fixture_draws_next',
                   'future_fixture_losses_next',
                   'future_fixture_goals_for_next',
                   'future_fixture_goals_against_next',
                   'future_fixture_goals_diff_next',
                   'future_fixture_played_next',
                   'future_fixture_yc_next',
                   'future_fixture_rc_next',
                   'future_fixture_team_unique_id_next_0',
                   'future_fixture_team_unique_id_next_1',
                   'future_fixture_team_unique_id_next_2',
                   'future_fixture_team_unique_id_next_3',
                   'future_fixture_team_unique_id_next_4',
                   'future_fixture_team_unique_id_next_5',
                   'future_fixture_team_unique_id_next_6',
                   'future_fixture_team_unique_id_next_7',
                   'future_fixture_team_unique_id_next_8',
                   'future_fixture_team_unique_id_next_9',
                   'future_fixture_team_unique_id_next_10',
                   'future_fixture_team_unique_id_next_11',
                   'future_fixture_team_unique_id_next_12',
                   'future_fixture_team_unique_id_next_13',
                   'future_fixture_team_unique_id_next_14',
                   'future_fixture_team_unique_id_next_15',
                   'future_fixture_team_unique_id_next_16',
                   'future_fixture_team_unique_id_next_17',
                   'future_fixture_team_unique_id_next_18',
                   'future_fixture_team_unique_id_next_19',
                   'future_fixture_team_unique_id_next_20',
                   'future_fixture_team_unique_id_next_21',
                   'future_fixture_team_unique_id_next_22',
                   'future_fixture_team_unique_id_next_23',
                   'future_fixture_team_unique_id_next_24',
                   'future_fixture_team_unique_id_next_25',
                   'future_fixture_team_unique_id_next_26',
                   'future_fixture_team_unique_id_next_27',
                   'future_fixture_team_unique_id_next_28',
                   'future_fixture_team_unique_id_next_29',
                   'future_fixture_team_unique_id_next_30']

response_columns = ['points_next']

X_train = data_train[feature_columns]
yy_train = data_train[response_columns]
unique_id_train = data_train[unique_id_column]

X_val = data_val[feature_columns]
yy_val = data_val[response_columns]
unique_id_val = data_val[unique_id_column]

X_test = data_test[feature_columns]
yy_test = data_test[response_columns]
unique_id_test = data_test[unique_id_column]

X_train, scaler = data_preprocesser.scale_features(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

model = LinearRegressionModel()
model.fit(X_train, yy_train)

yy_train_hat = model.predict(X_train)
yy_val_hat = model.predict(X_val)

RMSE = model.RMSE(yy_val.values, yy_val_hat)
print(RMSE)

plt.plot(yy_train, yy_train_hat, 'ob')
plt.plot(yy_val, yy_val_hat, 'xr')
plt.plot([0,30], [0,30], '--k')
plt.grid()
plt.xlabel('Ground Truth')
plt.ylabel('Prediction')
plt.show()


