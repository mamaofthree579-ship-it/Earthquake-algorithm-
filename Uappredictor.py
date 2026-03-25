import streamlit as st
import pandas as pd
import requests
import io
import numpy as np

# 1. Page Setup
st.set_page_config(page_title="Guardian Predictor", layout="wide")
st.title("The Guardians: Robust Stream Link")

# 2. Robust UAP Data Fetcher (CORGIS Mirror)
@st.cache_data
def get_uap_data():
    url = "https://corgis-edu.github.io"
    try:
        response = requests.get(url, timeout=10)
        # Using specific CORGIS column names found in their raw CSV
        df = pd.read_csv(io.StringIO(response.text), on_bad_lines='skip')
        
        # Explicit Mapping for CORGIS
        mapping = {
            'Location.Latitude': 'lat',
            'Location.Longitude': 'lon',
            'Data.Date.Time': 'time',
            'Location.City': 'city'
        }
        
        # Check if columns exist before renaming
        existing_cols = {k: v for k, v in mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)
        
        # Force numeric coordinates
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        return df.dropna(subset=['lat', 'lon']).head(1000) # Limit for speed
    except Exception as e:
        st.error(f"UAP Load Error: {e}")
        return pd.DataFrame()

# 3. Stable Seismic Feed (USGS GeoJSON)
def get_seismic_data():
    url = "https://earthquake.usgs.gov"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        points = []
        for f in data['features']:
            coords = f['geometry']['coordinates']
            points.append({
                'lat': coords[1], # Latitude is index 1
                'lon': coords[0], # Longitude is index 0
                'mag': f['properties']['mag'],
                'type': 'Seismic Trigger'
            })
        return pd.DataFrame(points)
    except Exception as e:
        # Fallback to an empty DF with correct columns
        return pd.DataFrame(columns=['lat', 'lon', 'mag', 'type'])

# 4. Main App Logic
uap_df = get_uap_data()
live_df = get_seismic_data()

# 5. Dashboard Display
if not uap_df.empty:
    st.success("UAP Stream: ONLINE")
    
    # Calculate System Activation (Simple overlap for testing)
    if not live_df.empty:
        st.success("Seismic Stream: ONLINE")
        # Combine for the map
        combined = pd.concat([
            uap_df[['lat', 'lon']].assign(type='Historical Node'),
            live_df[['lat', 'lon']].assign(type='Seismic Trigger')
        ])
        st.map(combined, color='type')
    else:
        st.warning("Seismic Stream: OFFLINE (Using UAP nodes only)")
        st.map(uap_df, color='#0000FF')
else:
    st.error("Planetary data streams are currently unreachable.")

# 6. Status Heartbeat
st.sidebar.markdown("### System Heartbeat")
st.sidebar.write(f"UAP Nodes Cached: {len(uap_df)}")
st.sidebar.write(f"Live Seismic Events: {len(live_df)}")
