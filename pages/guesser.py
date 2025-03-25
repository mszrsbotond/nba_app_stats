from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import commonallplayers
import datetime as dt
import pandas as pd
import streamlit as st

# get a random player
# find the matching id

# get all players
players_all = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0].dropna(how="any")

def get_random_player_stats():
    # get a random player
    players = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0].dropna(how="any")
    player = players.sample(n=1)
    return player
@st.cache_data
def get_player_stats():
    players = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0].dropna(how="any")
    return players

# find the matching id
@st.cache_data
def load_player_stats(id):
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=id).get_data_frames()[0].dropna(how="any")
        return player_info

def adjust_df(id):

    # adjust the dataframe 
    player_stats = load_player_stats(id)
    player_stats["BIRTHDATE"] = pd.to_datetime(player_stats["BIRTHDATE"], utc = True)
    player_stats["NAME"] = player_stats["FIRST_NAME"] + " " + player_stats["LAST_NAME"]
    player_stats["TEAM"] = player_stats["TEAM_CITY"] + " " + player_stats["TEAM_NAME"]
    player_stats["AGE"] = dt.datetime.now().year - player_stats["BIRTHDATE"].dt.year
    player_stats["HEIGHT"] = player_stats["HEIGHT"].str.replace("-", ".")
    player_stats = player_stats.astype({"AGE": "Int64", "HEIGHT": "float", "WEIGHT": "Int64", "JERSEY": "Int64"})
    active_players = player_stats[player_stats["GAMES_PLAYED_FLAG"] == "Y"]
    active_players = active_players[["NAME", "TEAM", "POSITION","AGE", "HEIGHT", "WEIGHT", "JERSEY"]]
    return active_players


if 'random_player_id' not in st.session_state:
    st.session_state.random_player_id = get_random_player_stats()["PERSON_ID"].values[0]

solution_player = adjust_df(st.session_state.random_player_id)
st.title("NBA Player Guesser")

def guess_a_player():
    # guess a player
    guessed_player = st.selectbox(
        f"Player", players_all["DISPLAY_FIRST_LAST"]
    )

    all_players = get_player_stats()
    guessed_player_id = all_players[all_players["DISPLAY_FIRST_LAST"] == guessed_player]["PERSON_ID"]
    guessed_player_stats = adjust_df(guessed_player_id)
    return guessed_player_stats

if 'already_guessed' not in st.session_state:
    st.session_state.already_guessed = []

guessed_player = guess_a_player()
styled_guessed_player = guessed_player.style.apply(
    lambda x: [
        'background-color: green' if col == "NAME" and x[col] == solution_player["NAME"].values[0] else
        'background-color: #a08a06' if col in ["AGE", "WEIGHT", "HEIGHT", "JERSEY"] and x[col] < solution_player[col].values[0] else
        'background-color: #410000' if col in ["AGE", "WEIGHT", "HEIGHT", "JERSEY"] and x[col] > solution_player[col].values[0] else
        'background-color: green' if col in ["AGE", "WEIGHT", "HEIGHT", "JERSEY"] and abs(x[col] - solution_player[col].values[0]) < 0.01 else
        ''
        for col in guessed_player.columns
    ], axis=1
).format(precision=1)

st.session_state.already_guessed.insert(0, styled_guessed_player)

i = 0
for guessed in (st.session_state.already_guessed):
    i += 1
    if i < 11:
        st.dataframe(guessed)
    else:
        st.write("You are out of guesses, the solution was:")
        solution_player
        break
    