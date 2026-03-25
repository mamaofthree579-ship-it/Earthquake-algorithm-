import streamlit as st
import pandas as pd
import requests
import io
import numpy as np

# 1. Haversine Distance (km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

# 2. Robust UAP Data Load (Standardizing Time)
@st.cache_data
def get_uap_data():
    url = "https://corgis-edu.github.io"
    try:
        response = requests.get(url, timeout=15)
        df = pd.read_csv(io.StringIO(response.text), on_bad_lines='skip', engine='python')
        df = df.rename(columns={'Location.Latitude': 'lat', 'Location.Longitude': 'lon', 'Location.City': 'city'})
        
        # Standardize Time to ISO 8601 UTC
        df['time'] = pd.to_datetime(df['Data.Date.Time'], errors='coerce', utc=True)
        return df.dropna(subset=['lat', 'lon', 'time'])
    except Exception as e:
        st.error(f"UAP Load Error: {e}")
        return pd.DataFrame()

# 3. Live Seismic Feed (Significant Triggers Only)
def get_seismic_data():
    url = "https://earthquake.usgs.gov"
    try:
        resp = requests.get(url, timeout=10).json()
        points = []
        for f in resp['features']:
            coords = f['geometry']['coordinates']
            points.append({
                'lat': coords[1], 'lon': coords[0], 
                'mag': f['properties']['mag'], 'place': f['properties']['place'],
                'time': f['properties']['time']
            })
        df = pd.DataFrame(points)
        # Convert USGS Epoch to ISO 8601 UTC
        df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
        return df
    except Exception as e:
        st.error(f"Seismic Load Error: {e}")
        return pd.DataFrame()

# 4. Main Predictor Logic
st.title("Guardian Predictor: Time-Synced Logic")
df_uap = get_uap_data()
live_stress = get_seismic_data()

if not live_stress.empty and not df_uap.empty:
    log_entries = []
    active_clusters = []
    
    # Filter for Significant Response (M5.5+)
    major_triggers = live_stress[live_stress['mag'] >= 5.5]
    
    for _, quake in major_triggers.iterrows():
        # Weighted Radius = (Mag^2) * 10
        radius = (quake['mag'] ** 2) * 10
        dist = haversine(quake['lat'], quake['lon'], df_uap['lat'], df_uap['lon'])
        matches = df_uap[dist <= radius].copy()
        
        if not matches.empty:
            matches['type'] = 'Activated Node'
            active_clusters.append(matches)
            log_entries.append(f"⚠️ **ALERT:** M{quake['mag']} near {quake['place']} (Synced: {quake['time'].strftime('%Y-%m-%d')}) triggered {len(matches)} nodes.")

    # 5. Display Components
    col1, col2 = st.columns([2, 1])
    with col1:
        if active_clusters:
            st.map(pd.concat([major_triggers.assign(type='Seismic Trigger')] + active_clusters), color='type')
        else:
            st.info("No active M5.5+ clusters detected.")
            st.map(live_stress.assign(type='Seismic Monitor'))
    
    with col2:
        st.subheader("System Activation Log")
        for entry in log_entries: st.write(entry)
else:
    st.info("Awaiting live planetary data streams...")
