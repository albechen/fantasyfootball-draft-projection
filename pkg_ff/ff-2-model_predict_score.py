# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # 1. Feature Extraction and Cleaning
#
# This notebook overviews the process of cleaning the raw data how the fantasy points are correlated with player stats (raw data from [Pro Football Reference](https://www.pro-football-reference.com/years/2000/fantasy.htm)). The main challenge was getting historical information aligned with each player – and being able to adjust how many years back the dataset will output.
#
# The final process inputs raw data on each player’s fantasy points and football stats from 2000 – 2019 and outputs a dataset that aligned their fantasy points in a single year with historical stats form X number of years past. Allowing each year's performance to be counted as a datapoint.
#
# Some constraints made were (1) rookies were excluded from selection, (2) only players with more than 8 games were included in the final dataset but all seasons were included for historical stats (3) Half – PPR was used as the metric, but it can be adjusted, and (4) player’s names were stripped of special symbols and prefix / suffix.
# %% [markdown]
# ## 1.1 Pulling Raw Data and Formating

# %%
import pandas as pd
import numpy as np
import re


# %%
def combine_df(start_year, end_year, scrim_or_fantasy):
    full_df = pd.DataFrame()
    for year in range(start_year, end_year + 1):
        path = "data_raw/%s.xlsx" % scrim_or_fantasy
        year_df = pd.read_excel(path, sheet_name=str(year))
        year_df["Year"] = year
        full_df = pd.concat([full_df, year_df])

    dl_path = "data_output/%s_%s_%s.csv" % (scrim_or_fantasy, start_year, end_year)
    full_df.to_csv(dl_path)

    return full_df


# %%
scrimmage = combine_df(2000, 2019, "scrimmage")
scrimmage.head()


# %%
fantasy = combine_df(2000, 2019, "fantasy")
fantasy.head()

# %% [markdown]
# ## 1.2 Cleaning and Combing Fantasy and Football Stats

# %%
scrimmage = pd.read_csv("data_output/scrimmage_2000_2019.csv", index_col=0)
fantasy = pd.read_csv("data_output/fantasy_2000_2019.csv", index_col=0)


def clean_names(df):
    name_list = []
    for name in df["Player"]:
        if name == "Mitch Trubisky":
            name = "Mitchell Trubisky"
        name_adj = str(name).replace("*", "").replace("+", "").replace(".", "")
        name_adj = name_adj.strip()
        name_adj = re.sub(" +", " ", name_adj)
        name_split = name_adj.split()
        for x in name_split:
            if x.lower() in ["iii", "ii", "iv", "v", "jr"]:
                name_split.remove(x)
        name_adj = " ".join(name_split)
        name_list.append(name_adj)
    df["Player"] = name_list
    return df


def cleaning_raw_df(df):
    # remove column headers in rows
    df = df[[(x != "Rk") for x in df["Rk"]]]

    # remove name symbols
    df = clean_names(df)

    # fill na values with zero.
    df = df.fillna(0)

    return df


def combine_fantasy_scrimmage(fantasy, scrimmage):
    # apply clenaing columns and dropping
    fantasy = cleaning_raw_df(fantasy)
    fantasy = fantasy.drop(
        columns=[
            "Rk",
            "REC_Y_R",
            "RSH_Y_A",
            "VBD_G",
            "PosRank_G",
            "OvRank_G",
            "Total_2PM_G",
            "Total_2PP_G",
        ]
    )
    scrimmage = cleaning_raw_df(scrimmage)
    scrimmage = scrimmage.drop(
        columns=[
            "Rk",
            "Tm",
            "Age",
            "Pos",
            "G",
            "GS",
            "RSH_Y_G",
            "RSH_A_G",
            "REC_R_G",
            "REC_R_G.1",
            "RSH_Lng",
            "REC_Lng",
        ]
    )

    # merge df and convert values to floats / strings
    combine = pd.merge(fantasy, scrimmage, how="outer", on=["Year", "Player"])
    num_df = combine.iloc[:, 3:46]
    num_df = num_df.apply(pd.to_numeric, errors="coerce")
    str_df = combine.iloc[:, 0:3].astype(str)
    full_df = pd.concat([str_df, num_df], axis=1, sort=False)
    full_df = full_df.dropna().reset_index(drop=True)
    return full_df


combine = combine_fantasy_scrimmage(fantasy, scrimmage)
print(combine.shape)
combine.columns


# %%
def remove_duplicat_players(df):
    df_split = df[["Player", "Year"]]
    df_split = df_split.loc[df_split.duplicated(keep=False)]
    df_split = df_split.reset_index()
    duplicate_list = df_split["index"].tolist()
    duplicate_df = df.ix[duplicate_list]
    duplicate_df = (
        duplicate_df.groupby(["Player", "Year"]).agg("max").reset_index(drop=True)
    )

    df = df.drop(df.index[duplicate_list])
    df = pd.concat([df, duplicate_df])
    df = df.reset_index(drop=True)

    return df


final_df = remove_duplicat_players(combine)
feq_players = final_df[
    (final_df["G"] >= 8)
    & ((final_df["FantPt_G"] + final_df["PPR_G"]) / 2 > 0.5)
    & (final_df["Position"] != "0")
    & (final_df["Position"] != 0)
]
feq_players.to_csv("data_output/0_years_stat_full.csv")
final_df.to_csv("data_output/stat_by_year.csv")
print(final_df.shape)
final_df.columns


# %%
final_df = pd.read_csv("data_output/stat_by_year.csv")


def fantasy_stats_split(df):
    base_split = df[["Year", "Player", "Tm"]]

    fantasy_split = df[["Position", "FantPt_G", "PPR_G", "DKPt_G", "FDPt_G", "G"]]
    fantasy_df = pd.concat([base_split, fantasy_split], axis=1, sort=False)
    fantasy_df = fantasy_df[
        (fantasy_df["G"] >= 8)
        & ((fantasy_df["FantPt_G"] + fantasy_df["PPR_G"]) / 2 > 0.5)
    ]
    fantasy_df = fantasy_df.drop(columns="G")

    hppr = list((df["FantPt_G"] + df["PPR_G"]) / 2)
    hppr = pd.DataFrame(hppr, columns=["HPPR_G"]).set_index(df.index[:])

    stat_split = pd.concat(
        [df[["Age", "G", "GS"]], df.iloc[:, 9:14], df.iloc[:, 16:44]],
        axis=1,
        sort=False,
    ).drop(columns=["Tm"])
    stat_df = pd.concat([base_split, stat_split], axis=1, sort=False)

    return fantasy_df, stat_df


fantasy_df, stat_df = fantasy_stats_split(final_df)
print(fantasy_df.columns)
print(stat_df.columns)
print(fantasy_df.shape)
print(stat_df.shape)
stat_df

# %% [markdown]
# ## 1.3 Joining Past Year’s Performance

# %%
def join_past_year_preformance(num_years_back, fantasy_df, stat_df, train_y_n):
    n = 1
    full_df = fantasy_df.copy()
    if train_y_n == "y":
        full_df = full_df[full_df["Year"] >= min(full_df["Year"]) + num_years_back]
    while n <= num_years_back:
        temp_stat = stat_df.copy()
        temp_stat["Year"] = temp_stat["Year"] + n
        suffix_temp = temp_stat.iloc[:, 2:41]
        suffix_temp = suffix_temp.add_suffix("-%s" % n)
        year_name = temp_stat.iloc[:, 0:2]

        temp_stat = pd.concat([year_name, suffix_temp], axis=1)
        full_df = pd.merge(full_df, temp_stat, how="left", on=["Year", "Player"])

        # check if they stayed on same team
        full_df[("Tm-%s" % n)] = np.where(full_df[("Tm-%s" % n)] != full_df["Tm"], 0, 1)
        n += 1
    return full_df


def remove_rookies(full_df):
    # remove rookies and fill blank years
    full_df = full_df.dropna(thresh=20)
    full_df = full_df.fillna(0)
    full_df = full_df[(full_df["Position"] != "0") & (full_df["Position"] != 0)]

    return full_df


train = remove_rookies(join_past_year_preformance(3, fantasy_df, stat_df, "y"))
print(list(train.columns))
train.head()


# %%
team_convert = pd.read_csv("data_raw/team_convert.csv")


def reset_team_names(team_convert, df):
    df = pd.merge(team_convert, df, how="right", on=["Tm"])
    df = df.drop(columns=["Tm"])
    df = df.rename(columns={"Team": "Tm"})
    return df


train = reset_team_names(team_convert, train)
train.head()

# %% [markdown]
# ## 1.4 X/Y Data Split for Model

# %%
def x_y_train_to_csv(years, fantasy_df, stat_df, y_n):
    train = join_past_year_preformance(years, fantasy_df, stat_df, y_n)
    train = remove_rookies(train)

    team_convert = pd.read_csv("data_raw/team_convert.csv")
    train = reset_team_names(team_convert, train)

    train.to_csv("data_output/%s_years_stat_full.csv" % years)

    train_x = train.drop(columns=["FantPt_G", "PPR_G", "DKPt_G", "FDPt_G"])
    train_x.to_csv("data_output/%s_years_x.csv" % years)

    train_y = list((train["FantPt_G"] + train["PPR_G"]) / 2)
    train_y = pd.DataFrame(train_y, columns=["HPPR_G"])
    train_y.to_csv("data_output/%s_years_y.csv" % years)

    return train, train_x, train_y


x_y_train_to_csv(4, fantasy_df, stat_df, "y")
x_y_train_to_csv(3, fantasy_df, stat_df, "y")
train, train_x, train_y = x_y_train_to_csv(2, fantasy_df, stat_df, "y")


# %%
print(train.shape)
train.head()


# %%
print(train_x.shape)
train_x.head()


# %%
print(train_y.shape)
train_y.head()

# %% [markdown]
# ## 1.5 2020 Players – X Data

# %%
stat_2020 = pd.read_csv("data_raw/FantasyPros_2020_Draft_Overall_Rankings.csv")


def player_team_pos(stat_2020):
    stat_2020 = stat_2020[["Overall", "Team", "Pos"]]
    stat_2020 = stat_2020[stat_2020["Team"] != "FA"]
    stat_2020["Pos"] = stat_2020["Pos"].str.replace("\d+", "")
    stat_2020 = stat_2020[(stat_2020["Pos"] != "K") & (stat_2020["Pos"] != "DST")]
    stat_2020["Year"] = 2020
    stat_2020 = stat_2020.rename(
        columns={"Overall": "Player", "Team": "Tm", "Pos": "Position"}
    )
    stat_2020 = clean_names(stat_2020)
    stat_2020 = stat_2020[["Tm", "Year", "Player", "Position"]]
    return stat_2020


test_2020 = player_team_pos(stat_2020)
test_2020.head()


# %%
test_2020 = join_past_year_preformance(2, test_2020, stat_df, "n")
test_2020 = remove_rookies(test_2020)
test_2020.to_csv("data_output/2020_x.csv")
print(test_2020.shape)
test_2020.head()


# %%
