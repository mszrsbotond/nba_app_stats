import streamlit as st
import pandas as pd


st.title("NBA Stats by \nmszrsbotond")
# load in the database
def load_data():
    df = pd.read_csv(r"database_24_25.csv")
    df = df.drop(columns=["Opp", "Res", "FT%"])
    return df.round(2)


df = load_data()
df["3P%"] = (df["3P"] / df["3PA"]).round(2) * 100
df["FG%"] = (df["FG"] / df["FGA"]).round(2) * 100
df_player_index = df.set_index("Player")
df_group = df_player_index.drop(columns=["Data", "Tm"])
df_group = df_group.groupby("Player").mean().round(2).sort_values(by="GmSc", ascending=False)


# Top 5 players by stat

# choose the stat
top5_stat = st.selectbox(
    "Stat", df_group.columns
)
# show title
f"Top 5 Players by {top5_stat}"

# create the correct dataframe
top5 = df_group.sort_values(by=top5_stat, ascending=False).head(5)

# style the dataframe
top5_styled = top5.style.set_properties(subset=[top5_stat], **{'background-color': '#22669e'}).format(precision=2)

# show the dataframe
top5_styled



# Chosen Player Stats
#  choose player
chosen_player = st.selectbox(
    "Player", df_group.index
)

# show title
f"{chosen_player} 2024-2025 Stats"

# create dataframe
player_stats_frame = df_group[df_group.index == chosen_player]
# show dataframe
player_stats_frame

# choose stat to show on linechart
stat_linechart = st.selectbox(
    "Stat to show", df_group.columns
)
#create dataframe all games through season
player_all_games = df_player_index[df_player_index.index == chosen_player][[stat_linechart, "Data"]]
player_all_games = player_all_games.set_index("Data")
st.line_chart(player_all_games)

# Teams

# Top 5 team in chosen category
# total games per team
team_games_played = df.groupby("Tm")["Data"].nunique()

# group by team and total stats sum
teams_grouped_total_stats = df.drop(columns=["Data", "Player"]).groupby("Tm").sum()
# divide total by number of games
teams_final_stats = teams_grouped_total_stats.div(team_games_played, axis=0)
# convert percentages to the correct format
teams_final_stats[["FG%", "3P%"]] = teams_final_stats[["FG%", "3P%"]] / 10
# round the final and display it
teams_final_stats = teams_final_stats.round(2)


# get which start to short by
top5_team_stat = st.selectbox(
    "Stat for team", df_group.columns
)

# short by given stat
top5_team = teams_final_stats.sort_values(by=top5_team_stat, ascending=False).head(5)
top5_team_styled = top5_team.style.set_properties(subset=[top5_team_stat], **{'background-color': '#22669e'}).format(precision=2)
top5_team_styled

# Choosen team stat
chosen_team = st.multiselect(
    "Choose Team", list(teams_final_stats.index), ["BOS"]
)

# chosen team stat and show it
teams_stats = teams_final_stats[teams_final_stats.index.isin(chosen_team)]
teams_stats

#chose which stat to show
chosen_stat = st.multiselect(
    "Choose Stat to show", list(teams_stats.columns), ["PTS"]
)

# bar chart PTS, AST, TRB for chosen teams
stats_to_bar = teams_stats[chosen_stat]
st.bar_chart(stats_to_bar.T, stack=False)

