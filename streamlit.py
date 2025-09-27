import streamlit as st
import pandas as pd
import time
import requests

def get_servers(place_id):
    url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"
    return requests.get(url).json().get("data", [])
st.set_page_config(page_title="Ro-Live",layout="wide")
st.title("Live Player Count")
p = st.text_input("Place Id")

if p:
    st.session_state["name"]=p
    val = st.session_state.get("name","")
    
    place_id = int(val)
    url = f"https://apis.roproxy.com/universes/v1/places/{place_id}/universe"

    resp = requests.get(url).json()
    rn = time.time()
    universe_id = resp["universeId"]

    url2 = f"https://games.roproxy.com/v1/games?universeIds={universe_id}"

    data = requests.get(url2).json()["data"][0]

    st.write(f" PLACE ID: {val}")
    st.write("Name: " + data.get("name","Null"))
    st.write("Updated: " + data.get("updated","NULL"))
    st.write(f"Created: {data.get("created","NULL")}")
    st.write(f"Visits: {data.get("visits","NULL")}")
    st.write(f"Creator: {data.get("creator","NULL")}")
    st.write(f"MAXPLAYERS PER SERVER: {data.get("maxPlayers","NULL")}")
    st.write(f"Favorites: {data.get("favoritedCount","NULL")}")
    # # st.line_chart(data.get("visits") [rn])
    if "player_count" not in st.session_state:
        st.session_state.player_count = []
        st.session_state.time = []
        st.session_state.server = []
        st.session_state.visi = []
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
            time.sleep(35)
        except Exception as e:
            st.error(e)

