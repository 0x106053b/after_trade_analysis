import pandas as pd
import numpy as np
import json

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)
draft_tickets = pd.read_csv("player_moves/draft_tickets_2020s.csv")

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

def df4(teamName):
    df4 = []
    for idx, trade in enumerate(trade_info):
        for a in trade["playerA"]:
            if a["type"] == "player":
                df4.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["statizId"], a["name"]])
        for b in trade["playerB"]:
            if b["type"] == "player":
                df4.append([trade["id"], trade["date"], trade["teamB"], trade["teamB"], b["statizId"], b["name"]])
    df4 = pd.DataFrame(df4, columns=["id", "date", "from", "to", "statizId", "resource"])
    infielder = ["C", "1B", "2B", "3B", "4B", "SS"]
    outfielder = ["LF", "RF", "CF"]
    player_info["statizId"] = player_info["statizId"].astype(str)
    df4 = df4.merge(player_info, on="statizId")[["id", "date", "from", "to", "statizId", "이름", "주포지션"]]
    df4.loc[df4["주포지션"].isin(infielder), "주포지션_rough"] = "Infielder"
    df4.loc[df4["주포지션"].isin(outfielder), "주포지션_rough"] = "Outfielder"
    df4["주포지션_rough"] = df4["주포지션_rough"].fillna("Pitcher")
    df4.loc[df4["주포지션_rough"] == "Pitcher", "주포지션"] = "null"

    df4.loc[df4["from"] == teamName, "InOut"] = "OUT"
    df4.loc[df4["to"] == teamName, "InOut"] = "IN"
    df4["count"] = "All"
    df4 = df4.dropna(subset=["InOut"])
    return df4

def df5(teamName, tradeType):    
    df3_temp = df3()
    df5 = df3_temp.merge(draft_tickets, left_on=["id","to"], right_on=["id", "팀"])
    df5 = df5.loc[df5["trade type"] == tradeType]
    df5.loc[df5["from"] == teamName, "InOut"] = "OUT"
    df5.loc[df5["to"] == teamName, "InOut"] = "IN"
    df5 = df5.dropna()
    return df5

def df6(teamName):
    df3_temp = df3()
    df3_temp.loc[df3_temp["from"] == teamName, "InOut"] = "OUT"
    df3_temp.loc[df3_temp["to"] == teamName, "InOut"] = "IN"
    df6 = df3_temp.dropna()
    df6 = df6.loc[df6["trade type"] == "money", ["resource", "InOut" ]]
    df6["resource"] = df6["resource"].apply(lambda x : float(x[:-2]))
    return df6