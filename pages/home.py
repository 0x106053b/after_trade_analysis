import pandas as pd
import numpy as np
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px

dash.register_page(__name__, path='/')

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)

# df1 : 트레이드 ID, 트레이드 일시, 각 트레이드에 참여한 구단 (teamA, teamB) 데이터프레임
df1 = pd.DataFrame(list(map(lambda x : [x["id"], x["date"], x["teamA"], x["teamB"]], trade_info)),
    columns=["id", "date", "teamA", "teamB"])
df1["date"] = pd.to_datetime(df1["date"])

# df1_0 : 연도별 트레이드 횟수 데이터프레임
df1_0 = df1.pivot_table(df1, index=df1["date"].apply(lambda x : x.year), aggfunc="count")["id"]
fig1_0 = px.bar(df1_0, x=df1_0.index, y="id", labels=dict(date="Year", id="Count"))
fig1_0.update_traces(customdata=df1_0.index)
fig1_0.update_yaxes(range=[4, 9.5])

#df2 : 트레이드 선수별 트레이드 날짜, 이름, statizId, 원소속팀, 이적팀, 주포지션
trade_list = []
for trade in trade_info:
    for x in trade["playerA"]:
        if x["type"] == "player":
            trade_list.append([trade["date"], x["name"], x["statizId"], trade["teamA"], trade["teamB"]])
    for x in trade["playerB"]:
        if x["type"] == "player":
            trade_list.append([trade["date"], x["name"], x["statizId"], trade["teamB"], trade["teamA"]])

df2 = pd.DataFrame(trade_list, columns=["date", "name", "statizId", "원소속팀", "이적팀"])
df2["date"] = pd.to_datetime(df2["date"])
player_info["statizId"] = player_info["statizId"].astype(str)
df2 = df2.merge(player_info, on="statizId", how="left")[["date", "name", "statizId", "원소속팀", "이적팀", "주포지션"]]

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
        html.H4("2020s Overall Trades"),
        html.Div(
            [
                # 1. 연간 트레이드 건수
                # 2. 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 소속 팀 (수도권팀 색조처리)
                html.Div(
                    [
                        dcc.Graph(id="annual-trade-counts",
                            figure=fig1_0,
                            hoverData={"points" : [{"customdata" : 2024}]}),
                        dcc.Graph(id="annual-trade-counts-byteam")
                    ],
                    style={"display" : "inline-block", "width" : "49%"}
                ),

                # 3. 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 포지션
                html.Div([
                    dcc.Graph(id="annual-trade-counts-byposition")
                ], style={"display" : "inline-block", "width" : "49%"}),
            ]
        )
    ]
)

@callback(
    Output("annual-trade-counts-byteam", "figure"),
    Input("annual-trade-counts", "hoverData")
)
def update_annual_trade_counts_byteam(hoverData):
   selected_year = hoverData['points'][0]['customdata']
   df1_1 = df1[df1["date"].map(lambda x : x.year) == selected_year]
   capital_team = ["LG", "키움", "두산", "KT", "SSG"]
   colors = ["수도권팀" if x in capital_team else "비수도권팀" for x in df1_1["teamA"]]
   fig1_1 = px.histogram(df1_1["teamA"], color=colors, labels=dict(value="Team", id="Count"))
   fig1_1.update_yaxes(dtick=1)
   fig1_1.update_layout(height=225, showlegend=False)
   return fig1_1

@callback(
    Output("annual-trade-counts-byposition", "figure"),
    Input("annual-trade-counts", "hoverData")
)
def update_annual_trade_counts_byposition(hoverData):
    selected_year = hoverData['points'][0]['customdata']
    df1_2 = df2[df2["date"].map(lambda x : x.year) == selected_year]
    fig1_2 = px.pie(labels=df1_2["주포지션"].value_counts().index, values=df1_2["주포지션"].value_counts().values)
    fig1_2.update_layout(height=400)
    return fig1_2