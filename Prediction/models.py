import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import torch
import torch.nn as nn
from collections import OrderedDict
import matplotlib.pyplot as plt


class ModelBase():

    def __init__(self):
        self.model = None

    def MSE(self, yy, yy_hat):

        return (yy-yy_hat).T@(yy-yy_hat)

    def SE(self, yy, yy_hat):

        return (1/yy.shape[0])*((yy-yy_hat).T@(yy-yy_hat))

    def RMSE(self, yy, yy_hat):

        return np.sqrt((1/yy.shape[0])*((yy-yy_hat).T@(yy-yy_hat)))

    def fit(self, X, yy):

        self.model.fit(X, yy)

    def predict(self, X):

        return self.model.predict(X)


class BaselineModel(ModelBase):

    def __init__(self):
        super().__init__()
        self.model = 'Baseline'
        self.mean = None

    def fit(self, yy):

        self.mean = np.mean(yy)

    def predict(self):

        return self.mean


class LinearRegressionModel(ModelBase):

    def __init__(self):
        super().__init__()
        self.model = LinearRegression()


class FullyConectedNeuralNetwork(nn.Module):

    def __init__(self, D_in ,H, D_out, n_layers, lr, batch_size, seed=1000):
        super().__init__()
        self.D_in = D_in
        self.H = H
        self.D_out = D_out
        self.n_layers = n_layers
        self.lr = lr
        self.batch_size = batch_size
        self.model = None
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.loss_fn = nn.MSELoss(reduction='sum')
        self.seed = seed
        torch.manual_seed(self.seed)

        self.build(self.D_in,
                      self.H,
                      self.D_out,
                      self.n_layers)

    def build(self, D_in ,H, D_out, n_layers):
        '''
        Build the neural network model
        :param D_in: Int --> No. of features
        :param H: Int --> No. of hidden units
        :param D_out: Int: --> No. of classes
        :param n_layers: Int: --> No. of Hidden Layers
        :return:  None
        '''

        torch.manual_seed(self.seed)
        model_architecture = OrderedDict()
        for layer in range(n_layers):
            if layer == 0:
                model_architecture['input'] = nn.Linear(D_in, H)
                model_architecture['relu_in'] = nn.ReLU()
            else:
                model_architecture['hidden_' + str(layer)] = nn.Linear(H, H)
                model_architecture['relu_' + str(layer)] = nn.ReLU()

        model_architecture['output'] = nn.Linear(H, D_out)

        self.model = nn.Sequential(model_architecture).cuda()

    def fit(self, x_train, y_train, x_val, y_val, n_epochs=100):
        '''
        Train the Neural Network model
        :param x_train: Numpy array --> Training data
        :param y_train: Numpy array --> Training data class labels
        :param x_val: Numpy array --> Validation data
        :param y_val: Numpy array --> Validation data class labels
        :param x_val_ss: Numpy array --> Another source of validation data
        :param y_val_ss: Numpy array --> Another source of validation data labels
        :param x_val_r: Numpy array --> Another source of validation data
        :param y_val_r: Numpy array --> Another source of validation data labels
        :param n_epochs: Int --> No. of maximum epoch to run the model, note that early stopping using x_val and y_val
        :return: None
        '''
        torch.manual_seed(self.seed)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        n_batches = int(x_train.shape[0] / self.batch_size)
        x_train = torch.tensor(x_train).float()
        x_train = x_train.to(self.device)
        y_train = torch.tensor(y_train).float()
        y_train = y_train.to(self.device)
        x_val = torch.tensor(x_val).float()
        x_val = x_val.to(self.device)

        self.MSE_min = 0
        self.epoch_max = 0
        self.n_epochs = n_epochs
        flag_stop = False
        MSE_val_list = []
        epoch = 0

        while (flag_stop is False) and (epoch <= self.n_epochs):
            loss_epoch = 0
            for batch in range(n_batches):
                x_train_batch = x_train[batch*self.batch_size:(batch+1)*self.batch_size, :]
                y_train_batch = y_train[batch*self.batch_size:(batch+1)*self.batch_size]
                # Forward pass: compute predicted y by passing x to the model.
                y_pred = self.model(x_train_batch)

                # Compute and print loss.
                loss = self.loss_fn(y_pred, y_train_batch)
                loss_epoch += loss

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            y_pred_val = self.predict(x_val)
            MSE_val = self.score(y_val, y_pred_val)
            MSE_val_list.append(MSE_val)
            if MSE_val <= self.MSE_min:
                    self.MSE_min = MSE_val
                    self.epoch_max = epoch

            if len(MSE_val_list) >= 500:
                    if np.mean(MSE_val_list[-250:]) >= np.mean(MSE_val_list[-500:-250]):
                        flag_stop = True

            if epoch % 10 == 0:
                print(epoch, (loss_epoch/n_batches).cpu().detach().numpy(), MSE_val)

            self.epoch = epoch
            epoch += 1

    def predict(self, x):
        '''
        Make predictions on an unknown data set
        :param x: Numpy array --> Data set to label
        :return: Tensor --> Class labels
        '''
        torch.manual_seed(self.seed)
        if torch.is_tensor(x) is False:
            x = torch.tensor(x).float()
            x = x.to(self.device)
        return self.model(x).cpu().detach().numpy()

    def score(self, y, y_pred):
        '''
        Calculate the F1 score
        :param y: class labels
        :param y_pred: predicted class labels
        :return: float --> f1 score
        '''
        torch.manual_seed(self.seed)
        if torch.is_tensor(y_pred) is True:
            y_pred = y_pred.cpu().detach().numpy()
        return self.MSE(y, y_pred)

    def MSE(self, yy, yy_hat):

        return (yy-yy_hat).T@(yy-yy_hat)

    def SE(self, yy, yy_hat):

        return (1/yy.shape[0])*((yy-yy_hat).T@(yy-yy_hat))

    def RMSE(self, yy, yy_hat):

        return np.sqrt((1/yy.shape[0])*((yy-yy_hat).T@(yy-yy_hat)))




class LSTM(nn.Module):
    def __init__(self, input_size, output_size=1, hidden_dim=50, n_layers=1, lr=0.001):
        super(LSTM, self).__init__()

        # Defining some parameters
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.lr = lr

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.lstm = nn.LSTM(input_size, hidden_dim).cuda()
        # Fully connected layer
        self.fc = nn.Linear(hidden_dim, output_size).cuda()

        self.hidden_cell = (torch.zeros(1,1,self.hidden_dim).to(self.device),
                            torch.zeros(1,1,self.hidden_dim).to(self.device))



    def forward(self, x):

        lstm_out, self.hidden_cell = self.lstm(x.view(len(x) ,1, -1), self.hidden_cell)
        predictions = self.fc(lstm_out.view(len(x), -1))
        return predictions


    # def fit(self, X_train, yy_train, unique_id_df, epochs=100):
    #
    #     torch.manual_seed(self.seed)
    #
    #     model = LSTM()
    #     loss_function = nn.MSELoss()
    #     optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)
    #
    #     n_batches = int(X_train.shape[0] / self.batch_size)
    #     unique_ids = unique_id_df.unique()
    #
    #     # Instantiate the model with hyperparameters
    #
    #     # We'll also set the model to the device that we defined earlier (default is CPU)
    #     model = self.model.to(self.device)
    #
    #     # Define hyperparameters
    #     n_epochs = 100
    #     lr=0.01
    #
    #     # Define Loss, Optimizer
    #     criterion = nn.CrossEntropyLoss()
    #     optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    #
    #     for epoch in range(epochs):
    #         for unique_id in unique_ids:
    #             X_seq = X_train[unique_id_df['unique_id']==unique_id].values
    #             yy_seq = yy_train[unique_id_df['unique_id']==unique_id].values
    #             X_seq = torch.tensor(X_seq).float()
    #             X_seq = X_seq.to(self.device)
    #             yy_seq = torch.tensor(yy_seq).float()
    #             yy_seq = yy_seq.to(self.device)
    #             optimizer.zero_grad() # Clears existing gradients from previous epoch
    #             #input_seq = input_seq.to(device)
    #             output, hidden = model(input_seq)
    #             output = output.to(device)
    #             target_seq = target_seq.to(device)
    #             loss = criterion(output, target_seq.view(-1).long())
    #             loss.backward() # Does backpropagation and calculates gradients
    #             optimizer.step() # Updates the weights accordingly



