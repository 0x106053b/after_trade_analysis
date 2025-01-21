import pandas as pd
import numpy as np
import warnings
import json
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback, dash_table, callback_context
import plotly.express as px
from assets.dataframe import *
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('mode.chained_assignment',  None)

dash.register_page(__name__, path='/team')
team_list = ["KIA", "삼성", "LG", "두산", "SSG", "KT", "롯데", "한화", "NC", "키움"]
buttons = [html.Button(x, id=f"{x}-button", className="button_unclicked", n_clicks=0) for x in team_list]

section1 = html.Div(
    [
        html.Div(id="section1")
    ]
)

layout = html.Div(
    [
        html.Div(buttons, id="grid-wrapper"),
        section1,
    ]
)

@callback(
    [Output(f"{x}-button", "className") for x in team_list],
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def button_active_color(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    return [
        "button_clicked" if triggered_id == f"{x}-button" else "button_unclicked" for x in team_list
    ]

@callback(
    Output("section1", "children"),
    [Input(f"{x}-button", "n_clicks") for x in team_list]
)
def update_dashboard(*team):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id.find('-') < 0:
        return html.P('''
                Click the team button to see the results of each team's trade.
                ''', className="lead", style={"color" : "gray", "text-align" : "center", "margin-top" : 200})

    else:
        teamName = triggered_id[:triggered_id.find('-')]
        df = df4(teamName)
        fig = px.icicle(df, path=["count", "InOut", "주포지션_rough", "주포지션"])
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin=dict(l=25, r=25, t=25, b=25))
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
                    html.Div(dcc.Graph(figure=fig, style={"height" : "100%"}), className="box", style={"width" : "50%"}),
                    html.Div([card_in_draft, card_out_draft, card_in_money, card_out_money], id="grid-wrapper2")
                ], style={"display" : "flex", "justify-content" : "space-between", "height" : "400px"})
            ]
        )