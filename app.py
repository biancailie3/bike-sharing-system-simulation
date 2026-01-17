import streamlit as st
import simpy
import pandas as pd
import folium
from streamlit_folium import st_folium
import logic

# Configurare pagină
st.set_page_config(layout="wide", page_title="EcoRide Business Dashboard")
st.title("🚲 EcoRide Timișoara: Simulare & Business")

# --- 1. CONFIGURARE (SIDEBAR) ---
st.sidebar.header("Setări Simulare")

if 'simulare_activa' not in st.session_state:
    st.session_state.simulare_activa = False
if 'rezultate_system' not in st.session_state:
    st.session_state.rezultate_system = None
if 'rezultate_stations' not in st.session_state:
    st.session_state.rezultate_stations = None

# Input-uri Utilizator
nr_zile = st.sidebar.slider("Durată (zile)", 1, 30, 5)
nr_biciclete = st.sidebar.slider("Flotă inițială per stație", 5, 30, 15)
interval_rebalansare = st.sidebar.slider("Frecvență Camion (min)", 10, 120, 45)

# Butonul de Start
if st.sidebar.button("▶️ Rulează Scenariul"):
    with st.spinner("Simulăm traficul și rerutările..."):
        env = simpy.Environment()
        stations = [
            logic.BikeStation("Piața Unirii", 25, nr_biciclete, 45.7579, 21.2289),
            logic.BikeStation("Gara de Nord", 20, nr_biciclete, 45.7503, 21.2003),
            logic.BikeStation("Complex Studențesc", 35, nr_biciclete, 45.7472, 21.2405),
            logic.BikeStation("Iulius Mall", 25, nr_biciclete, 45.7663, 21.2272)
        ]
        system = logic.BikeSharingSystem(env, stations, interval_rebalansare)
        
        def data_collector():
            while True:
                yield env.timeout(10) 
                for s in stations:
                    s.log_status()
                    
        env.process(data_collector())
        env.run(until=nr_zile * 720) 
        
        st.session_state.rezultate_system = system
        st.session_state.rezultate_stations = stations
        st.session_state.simulare_activa = True

# --- 2. DASHBOARD REZULTATE ---
if st.session_state.simulare_activa:
    sys = st.session_state.rezultate_system
    stations = st.session_state.rezultate_stations

    # --- A. MODUL FINANCIAR ---
    st.header("💰 Performanță Financiară")
    
    PRET_INCHIRIERE = 5     
    COST_CAMION_TUR = 15    
    
    venituri_totale = sys.happy_customers * PRET_INCHIRIERE
    minute_totale = nr_zile * 720
    numar_ture_camion = int(minute_totale / interval_rebalansare)
    costuri_totale = numar_ture_camion * COST_CAMION_TUR
    profit_net = venituri_totale - costuri_totale

    col_fin1, col_fin2, col_fin3 = st.columns(3)
    col_fin1.metric("Încasări Totale", f"{venituri_totale} RON", delta="Doar clienți mulțumiți")
    col_fin2.metric("Costuri Logistice", f"{costuri_totale} RON", delta="-Benzină", delta_color="inverse")
    col_fin3.metric("Profit Net", f"{profit_net} RON", 
                    delta="Profitabil" if profit_net > 0 else "Pierdere")

    st.divider()

    # --- B. KPI OPERAȚIONALI (AICI AM REPUS NUMERELE) ---
    st.subheader("📊 Statistici Clienți (Totaluri)")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    # 1. Cei care au plătit
    kpi1.metric("😊 Clienți Fericiți (Au plătit)", sys.happy_customers)
    
    # 2. Cei pierduți (nu au găsit bicicletă)
    kpi2.metric("❌ Pierduți (Lipsă Bicicletă)", sys.unhappy_no_bike, delta_color="inverse")
    
    # 3. Cei rerutați (au mers gratis)
    kpi3.metric("🆓 Rerutați Gratis (Lipsă Loc)", sys.unhappy_no_space, delta_color="inverse")

    st.divider()

    # --- C. HARTA ---
    st.subheader("📍 Harta Status Final")
    col_map, col_empty = st.columns([2, 1]) 
    
    with col_map:
        m = folium.Map(location=[45.755, 21.225], zoom_start=13)
        for s in stations:
            color = "green"
            if s.bikes < 2: color = "red"
            elif s.bikes > s.capacity - 2: color = "orange"
            
            folium.CircleMarker(
                location=[s.lat, s.lon], radius=15, 
                popup=f"<b>{s.name}</b><br>Biciclete: {s.bikes}/{s.capacity}",
                color=color, fill=True, fill_color=color
            ).add_to(m)
        st_folium(m, height=350, use_container_width=True)

    st.divider()

    # --- D. ANALIZĂ DETALIATĂ (GRAFICE) ---
    st.subheader("📈 Analiză Detaliată")
    tab1, tab2, tab3 = st.tabs(["📉 Evoluție Individuală", "📊 Top Aglomerație", "⚠️ Pierderi & Rerutări"])

    with tab1:
        st.caption("Selectează o stație pentru a vedea istoricul stocului.")
        nume_statie = st.selectbox("Alege Stația:", [s.name for s in stations])
        statie_selectata = next(s for s in stations if s.name == nume_statie)
        chart_data = pd.DataFrame({statie_selectata.name: statie_selectata.level_history})
        st.area_chart(chart_data, color="#3b8ed0")

    with tab2:
        st.caption("Media de biciclete disponibile.")
        data_medii = {s.name: sum(s.level_history)/len(s.level_history) for s in stations}
        st.bar_chart(pd.Series(data_medii), color="#90EE90") 

    with tab3:
        st.caption("Vizualizare cauze pierderi.")
        data_pierderi = {
            "Clienți Pierduți (Nu au găsit bicicletă)": sys.unhappy_no_bike,
            "Clienți Rerutați GRATIS (Nu au găsit loc)": sys.unhappy_no_space
        }
        st.bar_chart(pd.Series(data_pierderi), color="#ff4b4b")

else:
    st.info("👈 Configurează parametrii din stânga și apasă 'Rulează Scenariul'.")
