import pandas as pd
import numpy as np
import warnings
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, callback_context
import plotly.express as px
from assets.dataframe import *
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('mode.chained_assignment',  None)

dash.register_page(__name__, path='/team')
team_list = ["KIA", "삼성", "LG", "두산", "SSG", "KT", "롯데", "한화", "NC", "키움"]
team_buttons = [html.Button(x, id=f"{x}-button", className="button_unclicked", n_clicks=0) for x in team_list]
teamName = None

section1 = html.Div(
    [
        html.Div(id="section1")
    ]
)

section2 = html.Div(
    [
        html.Div(id="section2")
    ]
)

section3 = html.Div(
    [
        html.Div(id="section3")
    ]
)

section4 = html.Div(
    [
        html.Div(id="section4")
    ]
)

layout = html.Div(
    [
        html.Div(team_buttons, id="grid-wrapper"),
        section1,
        section2,
        section3,
        section4
    ]
)

@callback(
    [Output(f"{x}-button", "className") for x in team_list],
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def team_button_activation(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    return [
        "button_clicked" if triggered_id == f"{x}-button" else "button_unclicked" for x in team_list
    ]

@callback(
    Output("section1", "children"),
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def update_section1(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id.find('-') < 0:
        return html.P('''
                Click the team button to see the results of each team's trade.
                ''', className="lead", style={"color" : "gray", "text-align" : "center", "margin-top" : 200})

    else:
        teamName = triggered_id[:triggered_id.find('-')]
        df = df4(teamName)
        fig = px.icicle(df, path=["count", "InOut", "주포지션_rough", "주포지션"], 
            title=f"Proportion of Player Positions who trade out or trade in")
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=10),
                        title_x = 0.5, title_y = 0.98, title_font_size = 18, title_font_family = "Segoe UI")
        figure_data = fig["data"][0]
        mask = np.char.find(figure_data.ids.astype(str), "null") == -1
        figure_data.ids = figure_data.ids[mask]
        figure_data.values = figure_data.values[mask]
        figure_data.labels = figure_data.labels[mask]
        figure_data.parents = figure_data.parents[mask]

        df5_draft = df5(teamName, "draft")
        df5_draft_in = df5_draft.loc[df5_draft["InOut"] == "IN", ["팀", "선수"]]
        df5_draft_out = df5_draft.loc[df5_draft["InOut"] == "OUT", ["팀", "선수"]]

        df6_money = df6(teamName)
        df6_money_in = df6_money.loc[df6_money["InOut"] == "IN", "resource"]
        df6_money_out = df6_money.loc[df6_money["InOut"] == "OUT", "resource"]

        card_in_draft = dbc.Card(
            [
                dbc.CardHeader("[IN] Draft Picks", className="lead"),
                dbc.CardBody(
                    [
                        html.H4(f'{df5_draft_in.shape[0]} Picks', className="display-6"),
                        html.P(
                            [
                                ", ".join(list(df5_draft_in["선수"]))
                            ], style={"color" : "gray", "font-size" : "12px"}
                        )
                    ]
                )
            ], className="trade-card"
        )

        card_out_draft = dbc.Card(
            [
                dbc.CardHeader("[OUT] Draft Picks", className="lead"),
                dbc.CardBody(
                    [
                        html.H4(f'{df5_draft_out.shape[0]} Picks', className="display-6"),
                        html.P(
                            [
                                ", ".join(list(f"{df5_draft_out.iloc[idx]['선수']} ({df5_draft_out.iloc[idx]['팀']})" for idx in range(df5_draft_out.shape[0])))
                            ], style={"color" : "gray", "font-size" : "12px"}
                        )
                    ]
                )
            ], className="trade-card"
        )

        card_in_money = dbc.Card(
            [
                dbc.CardHeader("[IN] Cash Trades", className="lead"),
                dbc.CardBody(
                    [
                        html.H4("{:.2f}".format(df6_money_in.sum()*0.1) + ' Billion', className="display-6"),
                        html.P(
                            [
                                ", ".join(list(map(lambda x : str(x) + "억원", df6_money_in.sort_values())))
                            ], style={"color" : "gray", "font-size" : "12px"}
                        )
                    ]
                )
            ], className="trade-card"
        )

        card_out_money = dbc.Card(
            [
                dbc.CardHeader("[OUT] Cash Trades", className="lead"),
                dbc.CardBody(
                    [
                        html.H4("{:.2f}".format(df6_money_out.sum()*0.1) + ' Billion', className="display-6"),
                        html.P(
                            [
                                ", ".join(list(map(lambda x : str(x) + "억원", df6_money_out.sort_values())))
                            ], style={"color" : "gray", "font-size" : "12px"}
                        )
                    ]
                )
            ], className="trade-card"
        )

        return html.Div(
            [
                html.H3("2020s In/Out", className="display-6"),
                html.Small("Here's a look at the types of trades that came in and out for 2020s.", className="lead", style={"color" : "gray"}),
                html.Div([
                    html.Div(dcc.Graph(figure=fig, style={"height" : "100%"}), className="box", style={"width" : "55%"}),
                    html.Div([card_in_draft, card_out_draft, card_in_money, card_out_money], id="grid-wrapper2")
                ], style={"display" : "flex", "justify-content" : "space-between", "margin-bottom" : "80px"})
            ]
        )

@callback(
    Output("section2", "children"),
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def update_section2(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id.find('-') < 0:
        return None
    else:
        teamName = triggered_id[:triggered_id.find('-')]
        df_batter, df_pitcher = df7(teamName)
        df_batter["avg_war/144"] = round(df_batter["war_sum"] / df_batter["g_sum"] * 144, 3)
        df_batter.loc[df_batter["g_sum"] < 10, "avg_war/144"] = 0
        fig_batter = px.histogram(df_batter, x="InOut", y="avg_war/144", color="AB", barmode='group', height=300,
            title=f"WAR/144 Change of {teamName} Batters", category_orders={"InOut" : ["IN", "OUT"]},
            labels={"InOut" : "IN / OUT"}, text_auto=True,
            color_discrete_map={"In" : "#AB63FA", "Out" : "#B6E880"})
        fig_batter.update_layout(margin=dict(l=5, r=20, t=40, b=10),
                                title_x = 0.5, title_y = 0.99, title_font_size = 18, title_font_family = "Segoe UI")

        df_pitcher["avg_war/144"] = round(df_pitcher["war_sum"] / df_pitcher["g_sum"] * 144, 3)
        df_pitcher.loc[df_pitcher["g_sum"] < 10, "avg_war/144"] = 0
        fig_pitcher = px.histogram(df_pitcher, x="InOut", y="avg_war/144", color="AB", barmode='group', height=300,
            title=f"WAR/144 Change of {teamName} Pithcers", category_orders={"InOut" : ["IN", "OUT"]},
            labels={"InOut" : "IN / OUT"}, text_auto=True,
            color_discrete_map={"In" : "#AB63FA", "Out" : "#B6E880"})
        fig_pitcher.update_layout(margin=dict(l=5, r=20, t=40, b=10),
                                title_x = 0.5, title_y = 0.99, title_font_size = 18, title_font_family = "Segoe UI")

        return html.Div(
            [
                html.H3("Before vs After", className="display-6"),
                html.Small("Here's a look at how much SUM of WAR/144 has changed for In/Out Players.", className="lead", style={"color" : "gray"}),
                html.Br(),
                html.Small("For example, in case of 'IN' group, if ", className="lead", style={"color" : "gray"}),
                html.Span("purple ", className="lead", style={"color" : "#AB63FA", "fontWeight" : 500}),
                html.Small("is larger than ", className="lead", style={"color" : "gray"}),
                html.Span("green", className="lead", style={"color" : "#B6E880", "fontWeight" : 500}),
                html.Small(", the team has benefited in terms of WAR/144.", className="lead", style={"color" : "gray"}),
                html.Div([
                    html.Div(dcc.Graph(figure=fig_batter, style={"height" : "100%"}), className="box", style={"width" : "49%"}),
                    html.Div(dcc.Graph(figure=fig_pitcher, style={"height" : "100%"}), className="box", style={"width" : "49%"}),
                ], style={"display" : "flex", "justify-content" : "space-between", "margin-bottom" : "40px"})
            ]
        )

@callback(
    Output("section3", "children"),
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def update_section3(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    option_buttons = dcc.RadioItems(["Batter", "Pitcher"], "Batter")

    if triggered_id.find('-') < 0:
        return None
    else:
        return html.Div([
                html.Small("설명설명설명 옵션을선택해서 각선수의 변화를 확인하세여~", className="lead", style={"color" : "gray"}),
                html.Br(),
                dbc.ButtonGroup(
                [
                    dbc.Button("IN", id="in-button", className="option-button option-button-unclicked"),
                    dbc.Button("OUT", id="out-button", className="option-button option-button-unclicked"),
                ], style={"margin-top" : "15px", "margin-right" : "10px"}),
                dbc.ButtonGroup(
                [
                    dbc.Button("Batter", id="batter-button", className="option-button option-button-unclicked"),
                    dbc.Button("Pitcher", id="pitcher-button", className="option-button option-button-unclicked"),
                ], style={"margin-top" : "15px"})
            ])

@callback(
    [
        Output("in-button", "className"),
        Output("out-button", "className"),
    ],
    [
        Input("in-button", "n_clicks"),
        Input("out-button", "n_clicks")
    ]
)
def inout_button_activation(inbtn, outbtn):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "out-button":
        return ["option-button-unclicked", "option-button-clicked"]
    else:
        return ["option-button-clicked", "option-button-unclicked"]

@callback(
    [
        Output("batter-button", "className"),
        Output("pitcher-button", "className"),
    ],
    [
        Input("batter-button", "n_clicks"),
        Input("pitcher-button", "n_clicks")
    ]
)
def batpit_button_activation(inbtn, outbtn):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "pitcher-button":
        return ["option-button-unclicked", "option-button-clicked"]
    else:
        return ["option-button-clicked", "option-button-unclicked"]

@callback(
    Output("section4", "children"),
    [
        Input("in-button", "n_clicks"),
        Input("out-button", "n_clicks"),
        Input("batter-button", "n_clicks"),
        Input("pitcher-button", "n_clicks"),
        [State(f"{x}-button", "className") for x in team_list]
    ]
)
def update_section4(n_in, n_out, n_batter, n_pithcer, teams):
    teamName = team_list[teams.index("button_clicked")]
    ctx = dash.callback_context
    if ctx is None:
        return None
    else:
        InOut, BatPit = "IN", "batter" # default option (IN + Batter)
        if ctx.triggered_id == "in-button": InOut = "IN"
        elif ctx.triggered_id == "in-button": InOut = "OUT"
        elif ctx.triggered_id == "batter-button": BatPit = "batter"
        elif ctx.triggered_id == "pitcher-button": BatPit = "pitcher"
    df_batter, df_pitcher = df7(teamName)