import pandas as pd
import numpy as np
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

dash.register_page(__name__, path='/')

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)

# df1 : 트레이드 ID, 트레이드 일시, 각 트레이드에 참여한 구단 (teamA, teamB) 데이터프레임
df1 = pd.DataFrame(list(map(lambda x : [x["id"], x["date"], x["teamA"], x["teamB"]], trade_info)),
    columns=["id", "date", "teamA", "teamB"])
fig1 = px.histogram(np.ravel(df1[["teamA", "teamB"]]))

layout = html.Div(
    [
        dbc.Alert(
            [
                "All data on this dashboard is collected before 2025-01-10. All rights reserved to ",
                html.A("Sporki(Statiz).", href="https://statiz.sporki.com/", className="alert-link")
            ],
            id="alert-fade",
            className="lead",
            dismissable=True,
            fade=True,
            is_open=True,
            color="primary"
        ),
        html.Small('''
            Have you ever experienced letting the rookie player leave for another team?
            How about a player you loved enough to place his name on the back of your favorite uniform?
            Let's check the trade-related records made on 2020s KBO league to see if the traded player is doing well on another team as well!
        ''', className="lead", style={"color" : "gray"}),
        html.Button('\U0001f62d', style={"border" : "none", "background-color" : "white"}),
        html.Hr(),
        html.H4("How Many Trades are done?"),
        html.Div(
            [
                # 1. 연간 트레이드 건수
                # 1-1 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 포지션
                # 1-2 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 소속 팀 (수도권팀 색조처리)
                dcc.Graph(id="annual-trade-counts-byteam", figure=fig1)

                # 2. 팀별 트레이드 건수 (Sankey plot)
            ]
        )
    ]
)

# @app.callback(
#     Output('annual-trade-counts-byteam', 'children'),
#     Input('')
# )