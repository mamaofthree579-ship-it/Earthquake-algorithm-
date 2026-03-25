import streamlit as st
import pandas as pd
import requests
import io
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Guardian Predictor", layout="wide")
st.title("The Guardians: Robust Stream Link")

# 2. Universal Data Fetcher (Handles Header Variance)
@st.cache_data
def get_uap_data():
    url = "https://corgis-edu.github.io"
    try:
        response = requests.get(url, timeout=15)
        df = pd.read_csv(io.StringIO(response.text), on_bad_lines='skip')
        
        # FAILSAFE: Find columns by keyword instead of exact name
        lat_col = [c for c in df.columns if 'lat' in c.lower()][0]
        lon_col = [c for c in df.columns if 'lon' in c.lower()][0]
        
        # Explicitly rename for st.map
        df = df.rename(columns={lat_col: 'lat', lon_col: 'lon'})
        
        # Force numeric conversion and drop errors
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df.dropna(subset=['lat', 'lon']).head(1000)
    except Exception as e:
        st.error(f"UAP Stream Error: {e}")
        return pd.DataFrame()

# 3. Stable Seismic Feed (USGS Mirror)
def get_seismic_data():
    # Standard GeoJSON feed is more stable than the query API
    url = "https://earthquake.usgs.gov"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        points = []
        for f in data['features']:
            coords = f['geometry']['coordinates']
            points.append({
                'lat': coords[1], # Correct index for Latitude
                'lon': coords[0], # Correct index for Longitude
                'mag': f['properties']['mag'],
                'type': 'Seismic Trigger'
            })
        return pd.DataFrame(points)
    except Exception as e:
        return pd.DataFrame(columns=['lat', 'lon', 'mag', 'type'])

# 4. Interface and Logic
uap_df = get_uap_data()
live_df = get_seismic_data()

if not uap_df.empty:
    st.success("UAP Stream: ONLINE")
    
    if not live_df.empty:
        st.success("Seismic Stream: ONLINE")
        # Standardize for mapping
        uap_map = uap_df[['lat', 'lon']].copy()
        uap_map['type'] = 'Historical Node'
        
        combined = pd.concat([uap_map, live_df[['lat', 'lon', 'type']]])
        st.map(combined, color='type')
    else:
        st.warning("Seismic Feed unavailable; showing Historical Nodes only.")
        st.map(uap_df)
else:
    st.error("Wait for planetary sync...")
