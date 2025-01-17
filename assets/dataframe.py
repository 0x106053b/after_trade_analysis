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
    df2 = pd.DataFrame(trade_list, columns=["date", "name", "statizId", "from", "to"])
    df2["date"] = pd.to_datetime(df2["date"])
    return df2

def df3():
    trade_cases = []
    for idx, trade in enumerate(trade_info):
        for a in trade["playerA"]:
            if a["type"] == "player":
                trade_cases.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["type"], a["name"]])
            elif a["type"] == "draft":
                trade_cases.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["type"], a["round"]])
            elif a["type"] == "money":
                trade_cases.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["type"], a["amount"]])
        
        for b in trade["playerB"]:
            if b["type"] == "player":
                trade_cases.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["type"], b["name"]])
            elif b["type"] == "draft":
                trade_cases.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["type"], b["round"]])
            elif b["type"] == "money":
                trade_cases.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["type"], b["amount"]])

    df3 = pd.DataFrame(trade_cases, columns=["id", "date", "from", "to", "trade type", "resource"])
    return df3