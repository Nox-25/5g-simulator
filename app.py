import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

st.title("Cellular Tower Simulation & Coverage Map")

# Initialize session state for towers if not exists
if 'towers' not in st.session_state:
    st.session_state.towers = pd.DataFrame(columns=['lat', 'lon', 'power', 'frequency', 'height', 'type'])

# Sidebar for controls
with st.sidebar:
    st.header("Add/Simulate Tower")

    # Input parameters
    tower_type = st.selectbox("Tower Type", ["Macrocell", "Microcell", "Picocell", "Femtocell"])

    # Default values based on type
    defaults = {
        "Macrocell": {"power": 40.0, "freq": 800, "height": 30.0},
        "Microcell": {"power": 5.0, "freq": 1800, "height": 10.0},
        "Picocell": {"power": 1.0, "freq": 2100, "height": 5.0},
        "Femtocell": {"power": 0.1, "freq": 2600, "height": 3.0}
    }

    tx_power = st.slider("Transmit Power (W)", 0.1, 100.0, defaults[tower_type]["power"])
    frequency = st.selectbox("Frequency Band (MHz)", [700, 800, 900, 1800, 2100, 2600, 3500],
                           index=[700, 800, 900, 1800, 2100, 2600, 3500].index(defaults[tower_type]["freq"]))
    ant_height = st.slider("Antenna Height (m)", 2.0, 100.0, defaults[tower_type]["height"])

    st.markdown("---")
    st.markdown("### Output Parameters & Efficiency")

    # Simple free space path loss calculation simulation
    # Range roughly depends on power and frequency
    max_range = np.sqrt(tx_power) * (1000 / frequency) * 10
    efficiency = min(100, max(0, (tx_power / 100) * (2600 / frequency) * 100))

    st.metric("Estimated Max Range (km)", f"{max_range:.2f}")
    st.metric("Estimated Efficiency (%)", f"{efficiency:.1f}")
    st.metric("Coverage Area (sq km)", f"{np.pi * (max_range**2):.2f}")

    st.info("Click on the map to add a tower with these parameters, then click 'Add Selected Point as Tower'")

# Map layout
col1, col2 = st.columns([3, 1])

with col1:
    # Initialize map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    # Add existing towers to map
    for idx, row in st.session_state.towers.iterrows():
        # Calculate radius based on power (simplified representation)
        radius = np.sqrt(row['power']) * 2000 # in meters

        # Add tower marker
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"{row['type']} - {row['power']}W",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

        # Add coverage circle
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=radius,
            color="blue",
            fill=True,
            fill_opacity=0.2
        ).add_to(m)

    # Display map and capture clicks
    map_data = st_folium(m, width=800, height=600)

with col2:
    st.subheader("Map Actions")

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.write(f"Selected Location: \nLat: {lat:.4f}\nLon: {lon:.4f}")

        if st.button("Add Tower Here"):
            new_tower = pd.DataFrame([{
                'lat': lat,
                'lon': lon,
                'power': tx_power,
                'frequency': frequency,
                'height': ant_height,
                'type': tower_type
            }])
            st.session_state.towers = pd.concat([st.session_state.towers, new_tower], ignore_index=True)
            st.rerun()
    else:
        st.write("Click on the map to select a location")

    if not st.session_state.towers.empty:
        st.markdown("---")
        st.write(f"Total Towers: {len(st.session_state.towers)}")
        if st.button("Clear All Towers"):
            st.session_state.towers = pd.DataFrame(columns=['lat', 'lon', 'power', 'frequency', 'height', 'type'])
            st.rerun()
