import plotly.graph_objects as go
import pandas as pd
from assets.dataframe import *

def team_section4(teamName, InOut, BatPit, stat):
    df_batter, df_pitcher = df7(teamName)
    df = df_batter
    if BatPit == "Pitcher": df = df_pitcher

    players = df.loc[(df["InOut"] == InOut) & (df["AB"] == "After")].sort_values(stat, ascending=False).statizId
    data = {"line_x" : [], "line_y" : [], "before" : [], "after" : []}
    for player in players:
        player_name = df.loc[df["statizId"] == player, "resource"].values[0]
        avg_before = df.loc[(df["AB"] == "Before") & (df["statizId"] == player)][stat].values[0]
        avg_after = df.loc[(df["AB"] == "After") & (df["statizId"] == player)][stat].values[0]
        data["before"].extend([avg_before])
        data["after"].extend([avg_after])
        data["line_x"].extend([avg_before, avg_after, None])
        data["line_y"].extend([player_name, player_name, None])

    fig = go.Figure(
        data = [
            go.Scatter(
                x = data["before"],
                y = df.iloc[players.index]["resource"].to_list(),
                name = "Before traded",
                mode = "markers",
                marker=dict(
                    color="#00CC96",
                    size=13,
                )
            ),
            go.Scatter(
                x = data["after"],
                y = df.iloc[players.index]["resource"].to_list(),
                name = "After traded",
                mode = "markers",
                marker=dict(
                    color="#AB63FA",
                    size=13,
                )
            ),
            go.Scatter(
                x = data["line_x"],
                y = data["line_y"],
                mode = "markers+lines",
                showlegend = False,
                marker = dict(
                    symbol = "arrow",
                    color = "gray",
                    size = 12,
                    angleref = "previous",
                    standoff = 8
                )
            )
        ]
    )

    title_dict = {"wrc_avg" : "WRC", "avg_avg" : "Battting Average", "slg_avg" : "Slugging %", "ops_avg" : "OPS",
                    "era_avg" : "ERA", "win_avg" : "WINs per G", "hold_avg" : "HOLDs per G", "save_avg" : "SAVEs per G"}

    fig.update_layout(
        title=dict(text=f"Diff of {title_dict[stat]} Before/After Trades"),
        margin=dict(l=5, r=20, t=40, b=10),
        title_x = 0.5, title_y = 0.97, title_font_size = 18, title_font_family = "Segoe UI",
        height=300,
        legend_itemclick=False
    )

    return fig

def case_section3_batter1(df_batter):
    df_batter_before = df_batter[df_batter["AB"] == "Before"]
    df_batter_after = df_batter[df_batter["AB"] == "After"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = [list(df_batter_before["resource"].repeat(4)), ["avg", "ops", "ob", "slg"] * df_batter_before.shape[0]],
        y = df_batter_before[["avg_avg", "ops_avg", "obp_avg", "slg_avg"]].values.ravel(),
        name = "before",
        marker={"color" : "#00CC96"}
    ))

    fig.add_trace(go.Bar(
        x = [list(df_batter_after["resource"].repeat(4)), ["avg", "ops", "ob", "slg"] * df_batter_after.shape[0]],
        y = df_batter_after[["avg_avg", "ops_avg", "obp_avg", "slg_avg"]].values.ravel(),
        name = "after",
        marker={"color" : "#AB63FA"}
    ))

    fig.update_layout(
        title=dict(text=f"Diff of Main Batting Stats"),
        margin=dict(l=5, r=20, t=40, b=10),
        title_x = 0.5, title_y = 0.97, title_font_size = 18, title_font_family = "Segoe UI",
        height=300,
        legend_itemclick=False
    )
    
    return fig

def case_section3_pitcher1(df_pitcher):
    df_pitcher_before = df_pitcher[df_pitcher["AB"] == "Before"]
    df_pitcher_after = df_pitcher[df_pitcher["AB"] == "After"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = [list(df_pitcher_before["resource"].repeat(3)), ["win", "hold", "save"] * df_pitcher_before.shape[0]],
        y = df_pitcher_before[["win_avg", "hold_avg", "save_avg"]].values.ravel(),
        name = "before",
        marker={"color" : "#00CC96"}
    ))

    fig.add_trace(go.Bar(
        x = [list(df_pitcher_after["resource"].repeat(3)), ["win", "hold", "save"] * df_pitcher_after.shape[0]],
        y = df_pitcher_after[["win_avg", "hold_avg", "save_avg"]].values.ravel(),
        name = "after",
        marker={"color" : "#AB63FA"}
    ))

    fig.update_layout(
        title=dict(text=f"Diff of Main Pitching Achievements"),
        margin=dict(l=5, r=20, t=40, b=10),
        title_x = 0.5, title_y = 0.97, title_font_size = 18, title_font_family = "Segoe UI",
        height=300,
        legend_itemclick=False
    )

    return fig