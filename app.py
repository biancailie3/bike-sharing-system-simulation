import streamlit as st
import simpy
import pandas as pd
import folium
from streamlit_folium import st_folium
import logic  


st.set_page_config(layout="wide", page_title="Bike Sharing Timișoara")
st.title("🚲 Simulare Bike Sharing - Timișoara")


st.sidebar.header("Setări Simulare")

if 'simulare_activa' not in st.session_state:
    st.session_state.simulare_activa = False
if 'rezultate_system' not in st.session_state:
    st.session_state.rezultate_system = None
if 'rezultate_stations' not in st.session_state:
    st.session_state.rezultate_stations = None

nr_zile = st.sidebar.slider("Câte zile simulăm?", 1, 30, 10)
nr_biciclete = st.sidebar.slider("Biciclete inițiale per stație", 0, 20, 10)
interval_rebalansare = st.sidebar.slider("Interval camion (min)", 10, 120, 60)

if st.sidebar.button("▶️ Pornește Simularea"):
    
    with st.spinner("Se rulează simularea..."):
        env = simpy.Environment()
        
        stations = [
            logic.BikeStation("Piața Unirii", 20, nr_biciclete, 45.7579, 21.2289),
            logic.BikeStation("Gara de Nord", 15, nr_biciclete, 45.7503, 21.2003),
            logic.BikeStation("Complex Studențesc", 30, nr_biciclete, 45.7472, 21.2405),
            logic.BikeStation("Iulius Mall", 20, nr_biciclete, 45.7663, 21.2272)
        ]
        
        system = logic.BikeSharingSystem(env, stations, interval_rebalansare)
        
        # 2. Colectare date
        def data_collector():
            while True:
                yield env.timeout(10) # log at every 10 minutes
                for s in stations:
                    s.log_status()
                    
        env.process(data_collector())
        env.run(until=nr_zile * 720) # 720 minutes simulation
        
        # 3. save the data in memory
        st.session_state.rezultate_system = system
        st.session_state.rezultate_stations = stations
        st.session_state.simulare_activa = True  


if st.session_state.simulare_activa:
    
    # take out the data from memory
    sys = st.session_state.rezultate_system
    stations = st.session_state.rezultate_stations
    
    st.success("✅ Simulare completă!")

    # KPI Metrics
    col1, col2 = st.columns(2)
    col1.metric("Clienți Pierduți (Nu sunt biciclete)", sys.unhappy_no_bike, delta_color="inverse")
    col2.metric("Clienți Pierduți (Nu sunt locuri)", sys.unhappy_no_space, delta_color="inverse")

    st.divider()

    st.subheader("📍 Harta Timisoara - Statii biciclete")
    
    # map -  Timisoara
    m = folium.Map(location=[45.755, 21.225], zoom_start=13)
    
    for s in stations:
        # colours: red-full, orange-almost full, green-free
        color = "green"
        if s.bikes < 2: 
            color = "red"      
        elif s.bikes > s.capacity - 2: 
            color = "orange" 
        
        # stations=circles
        folium.CircleMarker(
            location=[s.lat, s.lon],
            radius=15,
            popup=f"<b>{s.name}</b><br>Biciclete: {s.bikes}/{s.capacity}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)
        
    # show map
    st_folium(m, width=1000, height=500)

    st.divider()

    # graphics
    st.subheader("📈 Evoluție Stoc Biciclete")
    chart_data = pd.DataFrame()
    for s in stations:
        chart_data[s.name] = s.level_history
    st.line_chart(chart_data)

else:
    st.info("👈 Apasă butonul 'Pornește Simularea' din meniul din stânga pentru a începe.")
