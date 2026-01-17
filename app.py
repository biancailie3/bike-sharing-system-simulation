# app.py
import streamlit as st
import simpy
import pandas as pd
import folium
from streamlit_folium import st_folium
import logic

st.set_page_config(layout="wide", page_title="EcoRide Dashboard")
st.title("🚲 EcoRide Timișoara: Analiză Performanță")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Configurare Simulare")
nr_zile = st.sidebar.slider("Durată (zile)", 1, 30, 7)
nr_biciclete = st.sidebar.slider("Biciclete/Stație (Start)", 5, 20, 10)
interval_rebalansare = st.sidebar.slider("Frecvență Camion (min)", 10, 120, 60)

if 'simulare_activa' not in st.session_state:
    st.session_state.simulare_activa = False

if st.sidebar.button("▶️ Rulează Simularea"):
    env = simpy.Environment()
    stations = [
        logic.BikeStation("Piața Unirii", 20, nr_biciclete, 45.7579, 21.2289),
        logic.BikeStation("Gara de Nord", 15, nr_biciclete, 45.7503, 21.2003),
        logic.BikeStation("Complex Studențesc", 30, nr_biciclete, 45.7472, 21.2405),
        logic.BikeStation("Iulius Mall", 20, nr_biciclete, 45.7663, 21.2272)
    ]
    system = logic.BikeSharingSystem(env, stations, interval_rebalansare)
    
    def data_collector():
        while True:
            yield env.timeout(10)
            for s in stations: s.log_status()
            
    env.process(data_collector())
    env.run(until=nr_zile * 720)
    
    st.session_state.rezultate_system = system
    st.session_state.rezultate_stations = stations
    st.session_state.simulare_activa = True

# --- AFIȘARE REZULTATE ---
if st.session_state.simulare_activa:
    sys = st.session_state.rezultate_system
    stations = st.session_state.rezultate_stations

    # Rândul de Metrici (KPIs)
    st.subheader("📊 Indicatori de Performanță")
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Clienți Fericiți 😊", sys.happy_customers)
    m2.metric("Fără Bicicletă ❌", sys.unhappy_no_bike, delta_color="inverse")
    m3.metric("Fără Loc Parcare 🅿️", sys.unhappy_no_space, delta_color="inverse")

    # Calcul Rata de Succes
    total = sys.happy_customers + sys.unhappy_no_bike
    success_rate = (sys.happy_customers / total * 100) if total > 0 else 0
    st.progress(success_rate / 100, text=f"Rata de succes a închirierilor: {success_rate:.1f}%")

    st.divider()

    # Hartă și Grafic în coloane
    col_map, col_chart = st.columns([1, 1])

    with col_map:
        st.subheader("📍 Status Stații")
        m = folium.Map(location=[45.755, 21.225], zoom_start=13)
        for s in stations:
            color = "green" if 2 < s.bikes < s.capacity - 2 else "red"
            folium.CircleMarker(
                location=[s.lat, s.lon],
                radius=15,
                popup=f"{s.name}: {s.bikes} biciclete",
                color=color, fill=True, fill_color=color
            ).add_to(m)
        st_folium(m, width=500, height=400)

    with col_chart:
        st.subheader("📈 Evoluție Stoc")
        chart_data = pd.DataFrame({s.name: s.level_history for s in stations})
        st.line_chart(chart_data, height=400)

else:
    st.info("Folosește meniul din stânga pentru a configura și porni simularea.")
