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

dash.register_page(__name__, path='/')

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
player_info["statizId"] = player_info["statizId"].astype(str)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)

# df1 : 트레이드 ID, 트레이드 일시, 각 트레이드에 참여한 구단 (teamA, teamB) 데이터프레임
df1 = df1()

# df1_0 : 연도별 트레이드 횟수 데이터프레임
df1_0 = df1.pivot_table(df1, index=df1["date"].apply(lambda x : x.year), aggfunc="count")["id"]

fig1_0 = px.line(df1_0, x=df1_0.index, y="id", 
        labels=dict(date="Year", id="Count"), markers=True, title="Annual Frequency of Trades")
fig1_0.update_traces(customdata=df1_0.index, marker_size=13)
fig1_0.update_yaxes(range=[4, 9.5])
fig1_0.update_layout(margin=dict(l=20, r=20, t=30, b=10),
    title_x = 0.5, title_y = 1.0, title_font_size = 20, title_font_family = "Segoe UI")

df2 = df2()
df2 = df2.merge(player_info, on="statizId", how="left")[["date", "name", "statizId", "from", "to", "주포지션"]]

df3 = df3()
df3_1 = pd.pivot_table(df3[["from", "to", "id"]], values="id", index="from", columns="to", aggfunc="count")
df3_1 = df3_1.fillna(0)
fig3 = px.imshow(df3_1, text_auto=True, aspect="auto", color_continuous_scale=[[0, 'white'], [1, 'gray']],
    title="Number of Players, Drafts, Cash Trades among Teams")
fig3.update_layout(margin=dict(l=20, r=20, t=50, b=10),
    title_x = 0.5, title_y = 1.0, title_font_size = 20, title_font_family = "Segoe UI")

df4 = df3.loc[:, ["date", "from", "to", "trade type", "resource"]]

section1 = html.Div(
            [
                # 1. 연간 트레이드 건수
                # 2. 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 소속 팀 (수도권팀 색조처리)
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="annual-trade-counts",
                                figure=fig1_0,
                                hoverData={"points" : [{"customdata" : 2020}]},
                                style={"height" : 265})
                            ],
                            className="box"
                        ),
                        html.Div(
                            [
                                dcc.Graph(id="annual-trade-counts-byteam",
                                style={"height" : 265}),
                            ],
                            className="box"
                        )
                    ],
                    style={"display" : "inline-block", "width" : "49%"}
                ),

                # 3. 연간 트레이드 건수 클릭 > 선택된 연도의 트레이드 선수 포지션 비율
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="annual-trade-counts-byposition",
                                style={"height" : 570})
                            ],
                            className="box"
                        )
                    ],
                    style={"display" : "inline-block", "width" : "49%", "height" : "100%"}
                ),
            ],
            style={"margin-bottom" : "80px", "height" : 628.2}
        )
section2 = html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="teamly-trade-counts",
                                            figure=fig3,
                                            hoverData={"points" : [{"x" : "KIA", "y" : "키움"}]},
                                            style={"height" : 400})
                            ], className="box"
                        )
                    ], style={"display" : "inline-block", "width" : "60%"}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dash_table.DataTable()
                            ], id="trade-resource-table", style={"margin" : "0px 10px"}
                        )
                    ], className="box", style={"display" : "inline-block", "width" : "39%", "overflow" : "hidden"}
                )
            ], style={"display" : "flex", "align-items": "stretch"}
        )

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
        html.H3("2020s Overall Trades", className="display-6"),
        html.Small("You can view annual statistics by hover the mouse on year.", className="lead", style={"color" : "gray"}),
        section1,

        html.H3("2020s Silk Roads among 10 Teams", className="display-6"),
        html.Small("You can click on the each cells to see the specific trade history.", className="lead", style={"color" : "gray"}),
        section2,
    ]
)

@callback(
    Output("annual-trade-counts-byteam", "figure"),
    Input("annual-trade-counts", "hoverData")
)
def update_annual_trade_counts_byteam(hoverData):
   selected_year = hoverData['points'][0]['customdata']
   df1_1 = df1[df1["date"].map(lambda x : x.year) == selected_year]
   teams = pd.concat([df1_1["teamA"], df1_1["teamB"]]).reset_index(drop=True)
   capital_team = ["LG", "키움", "두산", "KT", "SSG"]
   colors = pd.Series(["수도권팀" if x in capital_team else "비수도권팀" for x in teams])
   teamcolor = pd.concat([teams, colors], axis=1)
   teamcolor.columns = ["team", "color"]
   teamcolor = teamcolor.sort_values(by=["color", "team"])
   fig1_1 = px.histogram(teamcolor["team"], color=teamcolor["color"], text_auto=True,
                        color_discrete_map={"수도권팀" : "#AB63FA", "비수도권팀" : "#B6E880"}, 
                        labels=dict(value="Team", id="Count"), title="Teamly Frequency of Trades")
   fig1_1.update_yaxes(dtick=1)
   fig1_1.update_layout(height=240, showlegend=False, margin=dict(l=20, r=20, t=30, b=10),
    title_x = 0.5, title_y = 1.0, title_font_size = 20, title_font_family = "Segoe UI")
   return fig1_1

@callback(
    Output("annual-trade-counts-byposition", "figure"),
    Input("annual-trade-counts", "hoverData")
)
def update_annual_trade_counts_byposition(hoverData):
    selected_year = hoverData['points'][0]['customdata']
    df1_2 = df2[df2["date"].map(lambda x : x.year) == selected_year].reset_index(drop=True)
    infielder = ["C", "1B", "2B", "3B", "4B", "SS"]
    outfielder = ["LF", "RF", "CF"]

    df1_2["주포지션_내외야"] = \
        pd.Series(["Infielder" if x in infielder else "Outfielder" if x in outfielder else "None" for x in df1_2["주포지션"]])

    pd.pivot_table(df1_2, index=["주포지션_내외야", "주포지션"], aggfunc="count")
    df1_2 = df1_2.pivot_table(index=["주포지션_내외야", "주포지션"], aggfunc="count")["statizId"].reset_index()

    df1_2.loc[df1_2["주포지션_내외야"] == "None", "주포지션"] = None
    df1_2.loc[df1_2["주포지션_내외야"] == "None", "주포지션_내외야"] = "Pitcher"

    fig1_2 = px.sunburst(df1_2, path=["주포지션_내외야", "주포지션"], 
                        values="statizId", color="주포지션_내외야", names="주포지션_내외야",
                        title="Proportion of Traded Players' Positions")
    fig1_2.update_layout(margin=dict(l=20, r=20, t=30, b=20),
    title_x = 0.5, title_y = 1.0, title_font_size = 20, title_font_family = "Segoe UI")
    fig1_2.update_traces(textfont_size=15)

    return fig1_2

@callback(
    Output("trade-resource-table", "children"),
    Input("teamly-trade-counts", "hoverData")
)
def temp(hoverData):
    original_team, new_team = hoverData['points'][0]['y'], hoverData['points'][0]['x']
    return dash_table.DataTable(df4.loc[(df4["from"] == original_team) & (df4["to"] == new_team), :].to_dict('records'), 
            [{"name": i, "id": i} for i in df4.columns],
            style_table={'minWidth': '100%'},
            style_cell={
                'minWidth': '25px', 'width': '25px', 'maxWidth': '25px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'text-align' : 'center',
                'fontSize' : 13,
                'font-family' : "Segoe UI"
            },
            style_header={
            'backgroundColor': '#F4F4F2',
            'fontWeight': 'bold'
        })