import os
import sys
import urllib.request
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import warnings
import json
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, callback_context
import plotly.express as px
from assets.dataframe import *
from assets.figure import *

load_dotenv()

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('mode.chained_assignment',  None)

dash.register_page(__name__, path='/case')

year_list = [x for x in range(2020, 2025)]
team_list = ["KIA", "삼성", "LG", "두산", "SSG", "KT", "롯데", "한화", "NC", "키움"]

year_options = [{"label" : x, "value" : x} for x in year_list]
team_options = [{"label" : x, "value" : x} for x in team_list]

news_css_A = {"margin-top" : 10, "margin-bottom" : 10, "border-bottom" : "1px solid lightgray"}
news_css_B = {"margin-top" : 10, "margin-bottom" : 10}

section1 = html.Div(
    [
        html.Small("Choose a filter to compare the results of each trade.", className="lead", style={"color" : "gray"}),
        html.Br(),
        html.Div(
            [
                dcc.Dropdown(year_options, id="year-dropdown", placeholder="Select Year", style={"width" : 200, "margin-right" : 15}),
                dcc.Dropdown(team_options, id="team-dropdown", placeholder="Select Team", style={"width" : 200, "margin-right" : 15}),
                dcc.Dropdown(id="case-dropdown", placeholder="Select Specific Case", style={"width" : 600, "margin-right" : 15})
            ],
            id="section1",
            style={"display" : "flex", "justify-content" : "space-around", "width" : "70%", "margin-top" : 15, "margin-bottom" : 30}
        )
    ]
)

section2 = html.Div(
    id="case-section2",
    style={"margin-bottom" : 80}
)

section3 = html.Div(
    id="case-section3"
)

layout = html.Div(
    [
        section1,
        section2,
        section3
    ]
)

@callback(
    Output("case-dropdown", "options"),
    Input("year-dropdown", "value"),
    Input("team-dropdown", "value")
)
def yearteam_dropdown_activation(year, team):
    df = df3()
    case_dropdown_list = []
    df = df[(pd.to_datetime(df["date"]).apply(lambda x : x.year) == year) \
    & ((df["to"] == team) | (df["from"] == team))]
    for trade_id in df["id"].unique():
        case_df = df[df["id"] == trade_id]
        teamA, teamB = tuple(case_df.iloc[0][["from", "to"]].values)
        teamA_type = case_df.loc[case_df["from"] == teamA, "trade type"].values
        teamB_type = case_df.loc[case_df["from"] == teamB, "trade type"].values
        teamA_resource = case_df.loc[case_df["from"] == teamA, "resource"].values
        teamB_resource = case_df.loc[case_df["from"] == teamB, "resource"].values
        teamA_list, teamB_list = [], []
        for idx, trade_type in enumerate(teamA_type):
            if trade_type == "draft":
                teamA_list.append(teamA_resourcec[idx] + "라운드 지명권")
            elif trade_type == "money":
                teamA_list.append("현금" + teamA_resource[idx])
            else: teamA_list.append(teamA_resource[idx])
        
        for idx, trade_type in enumerate(teamB_type):
            if trade_type == "draft":
                teamB_list.append(teamB_resource[idx] + "라운드 지명권")
            elif trade_type == "money":
                teamB_list.append("현금" + teamB_resource[idx])
            else: teamB_list.append(teamB_resource[idx])
        
        trade_date = case_df.iloc[0]["date"]
        trade_case_str = f"{trade_date} {teamA : <3} ({', '.join(teamA_list)})  ↔  {teamB : <3} ({', '.join(teamB_list)})"
        case_dropdown_list.append({"label" : trade_case_str, "value" : trade_id})
    return case_dropdown_list

@callback(
    Output("case-section2", "children"),
    Input("case-dropdown", "value")
)
def case_dropdown_activation(trade_id):
    if trade_id is None:
        return html.P('''
                Select filter above to see the result of each trade case.
                ''', className="lead", style={"color" : "gray", "text-align" : "center", "margin-top" : 200})

    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

    df = df3()
    trade_str = " ".join(df.loc[df["id"] == trade_id, "resource"].values) + " 트레이드"

    encText = urllib.parse.quote(trade_str)
    url = "https://openapi.naver.com/v1/search/news?query=" + encText # JSON 결과

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    news_container = []

    if(rescode==200):
        response_body = response.read()
        for idx, x in enumerate(json.loads(response_body.decode('utf-8'))["items"][:5]):
            title = remove_tags(x["title"]) + "  "
            link = x["link"]
            description = remove_tags(x["description"])
            time = " ".join(x["pubDate"].split(" ")[:5])
            news_container.append(
                html.Div(
                    [
                        html.A(
                            [
                                html.Span(title, id="news_title", style={"color" : "black", "font-weight" : 500, "font-size" : "20px"}),
                                html.Span(time, style={"color" : "gray"}),
                            ], id="news_a", href=link, style={"text-decoration" : "none"}),
                        html.P(description, style={"color" : "#696969", "font-weight" : 300, "line-height" : "1.5"})
                    ],
                    style = news_css_B if idx == 4 else news_css_A
                )
            )
        return [
            html.H3("Related News Articles", className="display-6"),
            html.Small("Check out news articles about players' performances after the trade. \
                When you click on the news title, it goes to the news article page.", className="lead", style={"color" : "gray"}),
            html.Div(news_container, className="box", style={"padding-left" : 20, "padding-right" : 20})
        ]
            
    else:
        return html.Div([
            html.Small("Error! Please Try Again.", className="lead", style={"color" : "gray"})
        ])

@callback(
    Output("case-section3", "children"),
    Input("case-dropdown", "value")
)
def case_dropdown_activation2(trade_id):
    if trade_id is None:
        return None
    
    temp_df = df2()
    teamA, teamB = tuple(set(temp_df.loc[temp_df["id"] == trade_id, ["from", "to"]].values.ravel()))

    df_batter, df_pitcher = df7(teamA)
    df_batter = df_batter[df_batter["id"] == trade_id]
    df_pitcher = df_pitcher[df_pitcher["id"] == trade_id]

    df_batter_A = df_batter[df_batter["from"] == teamA]
    df_batter_B = df_batter[df_batter["to"] == teamA]
    df_pitcher_A = df_pitcher[df_pitcher["from"] == teamA]
    df_pitcher_B = df_pitcher[df_pitcher["to"] == teamA]

    fig_batter_A = case_section3_batter1(df_batter_A)
    fig_batter_B = case_section3_batter1(df_batter_B)

    fig_pitcher_A = case_section3_pitcher1(df_pitcher_A)
    fig_pitcher_B = case_section3_pitcher1(df_pitcher_B)

    return [
        html.H3("Compare A with B", className="display-6"),
        html.Small("Compare players' performance before and after the trade. Is this trade a success or a failure?", className="lead", style={"color" : "gray"}),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(teamB, style={"text-align" : "center", "font-weight" : 300, "font-size" : "30px", "margin-bottom" : 30}),
                        dcc.Graph(figure=fig_batter_A, style={"margin-bottom" : 50}) if df_batter_A.shape[0] != 0 else html.Div(),
                        dcc.Graph(figure=fig_pitcher_A,  style={"margin-bottom" : 50}) if df_pitcher_A.shape[0] != 0 else html.Div(),
                    ], className="box", style={"width" : "49%", "padding-left" : 25, "padding-right" : 25}
                ),
                html.Div(
                    [
                        html.H4(teamA, style={"text-align" : "center", "font-weight" : 300, "font-size" : "30px", "margin-bottom" : 30}),
                        dcc.Graph(figure=fig_batter_B, style={"margin-bottom" : 50}) if df_batter_B.shape[0] != 0 else html.Div(),
                        dcc.Graph(figure=fig_pitcher_B, style={"margin-bottom" : 50}) if df_pitcher_B.shape[0] != 0 else html.Div(),
                    ], className="box", style={"width" : "49%", "padding-left" : 25, "padding-right" : 25}
                )
            ],
            style = {"display" : "flex"}
        )
    ]