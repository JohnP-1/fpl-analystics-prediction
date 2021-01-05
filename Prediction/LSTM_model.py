import pandas as pd
import numpy as np
from preprocess import preprocess
import os.path as path
from models import LSTM
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import random

path_data = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'model_database.csv')
data = pd.read_csv(path_data)

seed = 1000
seed_test = 100

data_preprocesser = preprocess()

data_2020 = data[data['season']==2020]
data = data[data['season']!=2020]
data = data[data['minutes']!=0]

data = data[data['element_type_3']==1]
data_2020 = data_2020[data_2020['element_type_3']==1]

unique_ids = data['unique_id'].unique()

random.shuffle(unique_ids)
unique_ids = unique_ids[:int(len(unique_ids)*0.8)]
unique_ids_test = unique_ids[int(len(unique_ids)*0.8):]
unique_ids_train = unique_ids[:int(len(unique_ids)*0.7)]
unique_ids_val = unique_ids[int(len(unique_ids)*0.7):]

data_train = data[data['unique_id'].isin(unique_ids_train)]
data_val = data[data['unique_id'].isin(unique_ids_val)]
data_test = data[data['unique_id'].isin(unique_ids_test)]

unique_id_column = 'unique_id'

feature_columns = ['total_points']

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

X_train, scaler = data_preprocesser.scale_features(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

X_train = np.hstack((data_train['unique_id'].values.reshape((-1, 1)), X_train.reshape((-1, 1)), yy_train.reshape((-1, 1))))
columns_names = ['unique_id'] + feature_columns + response_columns
X_train = pd.DataFrame(X_train, columns=columns_names)

D_in = 1
H = 50
D_out = 1
n_layers = 3
lr = 2.5e-5
batch_size = 500

model = LSTM(D_in, output_size=1, hidden_dim=50, n_layers=1, lr=0.001).cuda()
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 150

unique_ids = data_train['unique_id'].unique()

for i in range(epochs):
    for unique_id in unique_ids:
        seq = X_train[X_train['unique_id']==unique_id][feature_columns].values
        labels = X_train[X_train['unique_id']==unique_id][response_columns].values
        seq = torch.tensor(seq).float()
        seq = seq.to(model.device)
        labels = torch.tensor(labels).float()
        labels = labels.to(model.device)
        optimizer.zero_grad()
        model.hidden_cell = (torch.zeros(1, 1, model.hidden_dim).to(model.device),
                        torch.zeros(1, 1, model.hidden_dim).to(model.device))

        # model.hidden_cell = model.hidden_cell.to(model.device)

        y_pred = model(seq)

        single_loss = loss_function(y_pred, labels)
        single_loss.backward()
        optimizer.step()

    if i%25 == 1:
        print(f'epoch: {i:3} loss: {single_loss.item():10.8f}')

print(f'epoch: {i:3} loss: {single_loss.item():10.10f}')



# model = FullyConectedNeuralNetwork(D_in ,H, D_out, n_layers, lr, batch_size, seed)
# model.fit(pc_scores[['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']].values, yy_train, pc_scores_val[['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']].values, yy_val, n_epochs=50000)
#
# X_2020 = data_2020[feature_columns].values
# X_2020 = scaler.transform(X_2020)
# yy_2020 = data_2020[response_columns].values
# unique_id_2020 = data_2020[unique_id_column].values
# round_2020 = data_2020['round'].values
#
# pc_scores_2020 = pca.transform(X_2020)
# pc_scores_2020 = pd.DataFrame(pc_scores_2020, columns=score_columns)
#
# yy_train_hat = (model.predict(pc_scores[['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']].values))
# yy_2020_hat = model.predict(pc_scores_2020[['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']].values)
#
# print(unique_id_2020.shape, data_2020['round'].values.reshape((-1, 1)).shape, X_2020.shape, yy_2020.shape, yy_2020_hat.shape)
#
# data_predictions = np.hstack((unique_id_2020.reshape((-1, 1)), round_2020.reshape((-1, 1)), X_2020, yy_2020, yy_2020_hat))
# data_predictions_columns = ['unique_id'] + ['round'] + feature_columns + response_columns + ['points_next_pred']
#
# data_predictions = pd.DataFrame(data_predictions, columns=data_predictions_columns)
#
# path_predictions = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'predictions.csv')
# data_predictions.to_csv(path_predictions, index=False)
#
# RMSE = model.RMSE(yy_2020, yy_2020_hat)
# print(RMSE)
#
# plt.plot(yy_train, yy_train_hat, 'ob')
# plt.plot(yy_2020, yy_2020_hat, 'xr')
# plt.plot([0,30], [0,30], '--k')
# plt.grid()
# plt.xlabel('Actual Points (Next GW)')
# plt.ylabel('Predicted Points (Next GW)')
# plt.show()


