import streamlit as st
import pandas as pd
import time
import requests
import os

def get_filtered_servers(place_id, max_ping=200, max_players=20):
    url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()
        servers = response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching server data: {e}")
        return []

    filtered = []
    for server in servers:
        ping = server.get("ping")
        playing = server.get("playing", 0)
        max_players_server = server.get("maxPlayers", 0)
        job_id = server.get("id")

        if ping is not None and ping <= max_ping and max_players_server <= max_players:
            filtered.append({
                "jobId": job_id,
                "ping": ping,
                "playing": playing,
                "maxPlayers": max_players_server
            })

    return filtered


def get_servers(place_id):
    url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"
    return requests.get(url).json().get("data", [])
st.set_page_config(page_title="Ro-Live",layout="wide")
st.title("Live Player Count")
p = st.text_input("Place Id")






if p:
    st.subheader("Server")
    ping = st.text_input("Ping (ms)")
    players_in_server = st.text_input("Players in Server")
    st.session_state["name"]=p
    val = st.session_state.get("name","")
    
    place_id = int(val)
    url = f"https://apis.roproxy.com/universes/v1/places/{place_id}/universe"

    resp = requests.get(url).json()
    rn = time.time()
    universe_id = resp["universeId"]

    url2 = f"https://games.roproxy.com/v1/games?universeIds={universe_id}"

    data = requests.get(url2).json()["data"][0]

    st.write(f"PLACE ID: {val}")
    st.write("Name: " + data.get("name","Null"))
    st.write("Updated: " + data.get("updated","NULL"))
    st.write("Created: " + data.get("created","NULL"))
    st.write("Visits: " + str(data.get("visits","NULL")))
    st.write("Creator: " + data.get("creator",{}).get("name","NULL"))
    st.write("MAXPLAYERS PER SERVER: " + str(data.get("maxPlayers","NULL")))
    st.write("Favorites: " + str(data.get("favoritedCount","NULL")))
    # # st.line_chart(data.get("visits") [rn])
    if "player_count" not in st.session_state:
        st.session_state.player_count = []
        st.session_state.time = []
        st.session_state.server = []
        st.session_state.visi = []
        st.session_state.plr = []
        st.session_state.id = []
    chart=st.empty()

    if players_in_server:
        st.write(f"Players entered: {players_in_server}")
        serv = get_filtered_servers(place_id, max_ping=int(ping), max_players=int(players_in_server))
        if serv:
            for s in servers:
                chart.write("JOBB:" + str(s['jobId']))
                
        

    t1 =st.empty()
    t = st.empty()
    chart_placeholder = st.empty()
    t2 = st.empty()

    while True:
        try:
            serv = get_servers(place_id)
            pl = [s["playing"] for s in serv]
            total = sum(pl)
            url3 = f"https://games.roproxy.com/v1/games?universeIds={universe_id}"

            data1 = requests.get(url3).json()["data"][0]
            vis = data1.get("visits",0)
            plr = data1.get("playing",0)
            ctime = pd.to_datetime("now")
            st.session_state.player_count.append(plr)
            st.session_state.time.append(ctime)
            st.session_state.server.append(total)
            st.session_state.visi.append(vis)
            df = pd.DataFrame({
                "Time": st.session_state.time,
                "Players": st.session_state.player_count

            })
            df.set_index("Time",inplace=True)
            # fig, ax = plt.subplots()
            # ax.plot(st.session_state.time,st.session_state.player_count)
            # ax.set_xlabel("Time")
            # ax.set_ylabel("Visit")
            chart_placeholder.line_chart(df)
            # time.sleep(10)
            # t1.write("Total Players Over Time")
            df1 = pd.DataFrame({
                "Time1": st.session_state.time,
                "Player": st.session_state.server

            })
            df1.set_index("Time1",inplace=True)

            t.line_chart(df1)

            df2 = pd.DataFrame({
                "Time2": st.session_state.time,
                "Visits": st.session_state.visi

            })
            df2.set_index("Time2",inplace=True)
            t2.line_chart(df2)
            t1.info("First Graph is total players over time! the other graph is active players and the other is visits!!")
            time.sleep(43)
        except Exception as e:
            st.error(e)




