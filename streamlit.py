import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=45000, limit=100, key="refresh")

def get_universe_id(place_id):
    url = f"https://apis.roproxy.com/universes/v1/places/{place_id}/universe"
    return requests.get(url).json().get("universeId")

def get_game_data(universe_id):
    url = f"https://games.roproxy.com/v1/games?universeIds={universe_id}"
    return requests.get(url).json()["data"][0]

def get_server_data(place_id):
    url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"
    return requests.get(url).json().get("data", [])

def get_filtered_servers(place_id, max_ping=200, max_players=20):
    servers = get_server_data(place_id)
    filtered = []
    for server in servers:
        ping = server.get("ping")
        playing = server.get("playing", 0)
        max_players_server = server.get("maxPlayers", 0)
        job_id = server.get("id")
        if ping is not None and ping <= max_ping and max_players_server <= max_players:
            filtered.append({
                "Job ID": job_id,
                "Ping (ms)": ping,
                "Players": playing,
                "Max Players": max_players_server
            })
    return filtered

st.set_page_config(page_title="Ro-Live", layout="wide")
st.title("Live Player Count")
st.subheader("Server")

place_id_input = st.text_input("Place ID")
ping_input = st.text_input("Ping Threshold (ms)", value="200")
players_input = st.text_input("Max Players Threshold", value="20")

if place_id_input:
    try:
        place_id = int(place_id_input)
        universe_id = get_universe_id(place_id)
        game_data = get_game_data(universe_id)

        st.write(f"**PLACE ID:** {place_id}")
        st.write(f"**Name:** {game_data.get('name', 'Null')}")
        st.write(f"**Updated:** {game_data.get('updated', 'NULL')}")
        st.write(f"**Created:** {game_data.get('created', 'NULL')}")
        st.write(f"**Visits:** {game_data.get('visits', 'NULL')}")
        st.write(f"**Creator:** {game_data.get('creator', {}).get('name', 'NULL')}")
        st.write(f"**Max Players per Server:** {game_data.get('maxPlayers', 'NULL')}")
        st.write(f"**Favorites:** {game_data.get('favoritedCount', 'NULL')}")

        if ping_input and players_input:
            max_ping = int(ping_input)
            max_players = int(players_input)
            filtered_servers = get_filtered_servers(place_id, max_ping, max_players)
            st.subheader("Filtered Servers")
            if filtered_servers:
                st.dataframe(pd.DataFrame(filtered_servers))
            else:
                st.info("No servers matched the criteria.")

        if "player_count" not in st.session_state:
            st.session_state.player_count = []
            st.session_state.time = []
            st.session_state.server = []
            st.session_state.visits = []

        servers = get_server_data(place_id)
        total_players = sum([s["playing"] for s in servers])
        current_data = get_game_data(universe_id)
        current_visits = current_data.get("visits", 0)
        current_playing = current_data.get("playing", 0)
        current_time = pd.to_datetime("now")

        st.session_state.player_count.append(current_playing)
        st.session_state.time.append(current_time)
        st.session_state.server.append(total_players)
        st.session_state.visits.append(current_visits)

        st.subheader("Live Charts")

        df_players = pd.DataFrame({
            "Time": st.session_state.time,
            "Players": st.session_state.player_count
        }).set_index("Time")
        st.line_chart(df_players)

        df_servers = pd.DataFrame({
            "Time": st.session_state.time,
            "Total Server Players": st.session_state.server
        }).set_index("Time")
        st.line_chart(df_servers)

        df_visits = pd.DataFrame({
            "Time": st.session_state.time,
            "Visits": st.session_state.visits
        }).set_index("Time")
        st.line_chart(df_visits)

        st.info("Charts show: active players, total players across servers, and visit count over time.")

    except Exception as e:
        st.error(f"Error: {e}")
