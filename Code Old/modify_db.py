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

path_data_2020 = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'player_database.csv')
path_data_backup = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'Processed', 'Backup', 'player_database_historic.csv')

data_2020 = pd.read_csv(path_data_2020)
data_backup = pd.read_csv(path_data_backup)

print(data_backup.shape, data_2020.shape)
print(list(data_backup.columns))
print(list(data_2020.columns))
