import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


class preprocess():

    def __int__(self):
        pass


    def select_features(self, data, columns):

        return data[columns]



    def select_responses(self, data, columns):

        return data[columns]


    def shuffle_dataset(self, data, seed=1000):

        np.random.seed(seed)
        idx = np.arange(0, data.shape[0])
        np.random.shuffle(idx)

        return data.iloc[idx, :]


    def split_dataset(self, data, split=0.7):

        N = data.shape[0]
        N_split = int(np.floor(split * N))

        data_1 = data.iloc[:N_split, :]
        data_2 = data.iloc[N_split:, :]

        return data_1, data_2


    def scale_features(self, data):

        scaler = StandardScaler()
        scaler.fit(data)
        data_scale = scaler.transform(data)

        return data_scale, scaler


