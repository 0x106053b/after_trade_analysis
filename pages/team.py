import pandas as pd
import numpy as np
import warnings
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
from assets.dataframe import df1, df2, df3
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('mode.chained_assignment',  None)

dash.register_page(__name__, path='/team')
team_list = ["KIA", "삼성", "LG", "두산", "SSG", "KT", "롯데", "한화", "NC", "키움"]
buttons = [html.Button(x, className="button_unclicked") for x in team_list]

layout = html.Div(
    [
        html.Small('''
            Click the team button to see the results of each team's trade.
        ''', className="lead", style={"color" : "gray"}),
        html.Hr(),
        html.Div(buttons, id="grid_wrapper")
    ]
)