import pandas as pd
import numpy as np
import json

player_info = pd.read_csv("player_stats/player_basic_info.csv", index_col = 0)
player_info["statizId"] = player_info["statizId"].astype(str)
with open("player_moves/trade_list_2020s.json", encoding='UTF8') as f:
    trade_info = json.load(f)
draft_tickets = pd.read_csv("player_moves/draft_tickets_2020s.csv")
draft_tickets["statizId"] = draft_tickets["statizId"].fillna(-1).astype(int).replace({-1: None})
draft_tickets["statizId"] = draft_tickets["statizId"].astype(str)

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
    df4_temp = []
    for idx, trade in enumerate(trade_info):
        for a in trade["playerA"]:
            if a["type"] == "player":
                df4_temp.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["statizId"], a["type"], a["name"]])
        for b in trade["playerB"]:
            if b["type"] == "player":
                df4_temp.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["statizId"], b["type"], b["name"]])
    df4 = pd.DataFrame(df4_temp, columns=["id", "date", "from", "to", "statizId", "trade type", "resource"])
    infielder = ["C", "1B", "2B", "3B", "4B", "SS"]
    outfielder = ["LF", "RF", "CF"]
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

def df7(teamName):
    df7_player = []
    df7_draft = []

    for idx, trade in enumerate(trade_info):
        for a in trade["playerA"]:
            if a["type"] == "player":
                df7_player.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["statizId"], a["type"], a["name"]])
            elif a["type"] == "draft":
                df7_draft.append([trade["id"], trade["date"], trade["teamA"], trade["teamB"], a["type"], a["round"]])
        for b in trade["playerB"]:
            if b["type"] == "player":
                df7_player.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["statizId"], b["type"], b["name"]])
            elif b["type"] == "draft":
                df7_draft.append([trade["id"], trade["date"], trade["teamB"], trade["teamA"], b["type"], b["round"]])

    df7_player = pd.DataFrame(df7_player, columns=["id", "date", "from", "to", "statizId", "trade type", "resource"])
    df7_draft = pd.DataFrame(df7_draft, columns=["id", "date", "from", "to", "trade type", "resource"])
    df7_draft = df7_draft.merge(draft_tickets, left_on=["id","to"], 
        right_on=["id", "팀"])[["id", "date", "from", "to", "statizId", "trade type", "선수"]]
    df7_draft.columns = ["id", "date", "from", "to", "statizId", "trade type", "resource"]
    df7_temp = pd.concat([df7_player, df7_draft])
    df7_temp = df7_temp.reset_index(drop=True)
    df7_temp = \
        df7_temp.merge(player_info, on="statizId")[["id", "date", "from", "to", "statizId", "trade type", "resource", "주포지션"]]

    df7_temp.loc[df7_temp["from"] == teamName, "InOut"] = "OUT"
    df7_temp.loc[df7_temp["to"] == teamName, "InOut"] = "IN"
    df7_temp = df7_temp.dropna(subset=["InOut"]).reset_index(drop=True)
    df7_before = df7_temp.copy()
    df7_after = df7_temp.copy()
    batter = ["1B", "2B", "3B", "SS", "LF", "CF", "RF", "C"]

    for idx in range(df7_temp.shape[0]):
        resource, statizId, position, tradeid, date = \
                tuple(df7_temp.loc[idx, ["resource", "statizId", "주포지션", "id", "date"]])
        if position in batter:
            regular_url = f"player_stats/annual_stats/regular/batting_stats/{resource}_{statizId}_annualStats.csv"
        elif position not in batter:
            regular_url = f"player_stats/annual_stats/regular/pitching_stats/{resource}_{statizId}_annualStats.csv"
        annual_df = pd.read_csv(regular_url, index_col=0)
        change_points = list(np.where(annual_df["Team"] != annual_df["Team"].shift())[0])[1:] + list((annual_df.shape[0],))
        trade_year = pd.to_datetime(date).year
        try :
            trade_year_index = np.where(annual_df["Year"] >= trade_year)[0][0]
            temp = np.where(trade_year_index <= change_points)[0][0]
            before_start = change_points[temp-1] if temp-1 >= 0 else 0
            before_end = change_points[temp]-1
            after_start = change_points[temp]
            after_end = change_points[temp+1]-1
            before_war_sum = round(annual_df.loc[before_start:before_end, "WAR"].sum(), 3)
            after_war_sum = round(annual_df.loc[after_start:after_end, "WAR"].sum(), 3)
            df7_before.loc[idx, "war_sum"] = before_war_sum
            df7_after.loc[idx, "war_sum"] = after_war_sum
        except:
            if annual_df.shape[0] > 0:
                before_start = 0
                before_end = 0
                after_start = 0
                after_end = 1
            continue

        if position in batter:
            before_g = annual_df.loc[before_start:before_end, "G"]
            after_g = annual_df.loc[after_start:after_end, "G"]
            if before_g.sum()==0 or after_g.sum() == 0:
                continue
            
            before_owar_sum = round(annual_df.loc[before_start:before_end, "oWAR"].sum(), 3)
            after_owar_sum = round(annual_df.loc[after_start:after_end, "oWAR"].sum(), 3)
            
            before_dwar_sum = round(annual_df.loc[before_start:before_end, "dWAR"].sum(), 3)
            after_dwar_sum = round(annual_df.loc[after_start:after_end, "dWAR"].sum(), 3)
            
            before_wrc_avg = round(annual_df.loc[before_start:before_end, "wRC+"].dot(before_g) / before_g.sum(), 3)
            after_wrc_avg = round(annual_df.loc[after_start:after_end, "wRC+"].dot(after_g) / after_g.sum(), 3)
            
            before_avg_avg = round(annual_df.loc[before_start:before_end, "AVG"].dot(before_g) / before_g.sum(), 3)
            after_avg_avg = round(annual_df.loc[after_start:after_end, "AVG"].dot(after_g) / after_g.sum(), 3)
            
            before_ops_avg = round(annual_df.loc[before_start:before_end, "OPS"].dot(before_g) / before_g.sum(), 3)
            after_ops_avg = round(annual_df.loc[after_start:after_end, "OPS"].dot(after_g) / after_g.sum(), 3)
            
            before_obp_avg = round(annual_df.loc[before_start:before_end, "OBP"].dot(before_g) / before_g.sum(), 3)
            after_obp_avg = round(annual_df.loc[after_start:after_end, "OBP"].dot(after_g) / after_g.sum(), 3)
            
            before_slg_avg = round(annual_df.loc[before_start:before_end, "SLG"].dot(before_g) / before_g.sum(), 3)
            after_slg_avg = round(annual_df.loc[after_start:after_end, "SLG"].dot(after_g) / after_g.sum(), 3)
            
            df7_before.loc[idx, "g_sum"] = before_g.sum()
            df7_after.loc[idx, "g_sum"] = after_g.sum()

            df7_before.loc[idx, "owar_sum"] = before_owar_sum
            df7_after.loc[idx, "owar_sum"] = after_owar_sum

            df7_before.loc[idx, "dwar_sum"] = before_dwar_sum
            df7_after.loc[idx, "dwar_sum"] = after_dwar_sum

            df7_before.loc[idx, "wrc_avg"] = before_wrc_avg
            df7_after.loc[idx, "wrc_avg"] = after_wrc_avg

            df7_before.loc[idx, "avg_avg"] = before_avg_avg
            df7_after.loc[idx, "avg_avg"] = after_avg_avg

            df7_before.loc[idx, "ops_avg"] = before_ops_avg
            df7_after.loc[idx, "ops_avg"] = after_ops_avg

            df7_before.loc[idx, "obp_avg"] = before_obp_avg
            df7_after.loc[idx, "obp_avg"] = after_obp_avg

            df7_before.loc[idx, "slg_avg"] = before_slg_avg
            df7_after.loc[idx, "slg_avg"] = after_slg_avg
        
        else:
            before_g = annual_df.loc[before_start:before_end, "G"].sum()
            after_g = annual_df.loc[after_start:after_end, "G"].sum()
            if before_g.sum()==0 or after_g.sum() == 0:
                continue

            before_ip = annual_df.loc[before_start:before_end, "IP"].sum()
            after_ip = annual_df.loc[after_start:after_end, "IP"].sum()
            if before_ip.sum()==0 or after_ip.sum() == 0:
                continue

            before_er = annual_df.loc[before_start:before_end, "ER"].sum()
            after_er = annual_df.loc[after_start:after_end, "ER"].sum()

            before_h = annual_df.loc[before_start:before_end, "H"].sum()
            after_h = annual_df.loc[after_start:after_end, "H"].sum()

            before_bb = annual_df.loc[before_start:before_end, "BB"].sum()
            after_bb = annual_df.loc[after_start:after_end, "BB"].sum()

            before_win_sum = annual_df.loc[before_start:before_end, "W"].sum()
            after_win_sum = annual_df.loc[after_start:after_end, "W"].sum()
            
            before_lose_sum = annual_df.loc[before_start:before_end, "L"].sum()
            after_lose_sum = annual_df.loc[after_start:after_end, "L"].sum()
            
            before_hold_sum = annual_df.loc[before_start:before_end, "HD"].sum()
            after_hold_sum = annual_df.loc[after_start:after_end, "HD"].sum()
            
            before_save_sum = annual_df.loc[before_start:before_end, "S"].sum()
            after_save_sum = annual_df.loc[after_start:after_end, "S"].sum()

            df7_before.loc[idx, "g_sum"] = before_g
            df7_after.loc[idx, "g_sum"] = after_g
            
            df7_before.loc[idx, "ip_sum"] = before_ip
            df7_after.loc[idx, "ip_sum"] = after_ip

            df7_before.loc[idx, "er_sum"] = before_er
            df7_after.loc[idx, "er_sum"] = after_er

            df7_before.loc[idx, "h_sum"] = before_h
            df7_after.loc[idx, "h_sum"] = after_h

            df7_before.loc[idx, "bb_sum"] = before_bb
            df7_after.loc[idx, "bb_sum"] = after_bb

            df7_before.loc[idx, "win_sum"] = before_win_sum
            df7_after.loc[idx, "win_sum"] = after_win_sum

            df7_before.loc[idx, "lose_sum"] = before_lose_sum
            df7_after.loc[idx, "lose_sum"] = after_lose_sum

            df7_before.loc[idx, "hold_sum"] = before_hold_sum
            df7_after.loc[idx, "hold_sum"] = after_hold_sum

            df7_before.loc[idx, "save_sum"] = before_save_sum
            df7_after.loc[idx, "save_sum"] = after_save_sum

    df7_before["AB"] = "Before"
    df7_after["AB"] = "After"
    df7_merged = pd.concat([df7_before, df7_after])

    pitcher_drop_cols = ['owar_sum', 'dwar_sum', 'wrc_avg', 'avg_avg', 'ops_avg', 'obp_avg', 'slg_avg']
    batter_drop_cols = ['ip_sum', 'er_sum', 'h_sum', 'bb_sum', 'win_sum', 'lose_sum','hold_sum', 'save_sum']

    df7_pitcher = df7_merged[df7_merged["주포지션"] == "P"].drop(columns=pitcher_drop_cols).reset_index(drop=True)
    df7_batter = df7_merged[df7_merged["주포지션"] != "P"].drop(columns=batter_drop_cols).reset_index(drop=True)
    return (df7_batter, df7_pitcher)
    