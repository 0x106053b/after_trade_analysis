import pandas as pd
import numpy as np
import json

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)

def df1():
    # df1 : 트레이드 ID, 트레이드 일시, 각 트레이드에 참여한 구단 (teamA, teamB) 데이터프레임
    df1 = pd.DataFrame(list(map(lambda x : [x["id"], x["date"], x["teamA"], x["teamB"]], trade_info)),
        columns=["id", "date", "teamA", "teamB"])
    df1["date"] = pd.to_datetime(df1["date"])
    return df1

def df2():
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
    return df2