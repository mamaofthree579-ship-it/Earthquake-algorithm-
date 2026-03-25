import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. Robust UAP Data Fetcher
@st.cache_data
def get_uap_data():
    url = "https://corgis-edu.github.io"
    try:
        response = requests.get(url, timeout=10)
        df = pd.read_csv(io.StringIO(response.text), on_bad_lines='skip')
        
        # SAFE COLUMN MAPPING: Look for whatever the date column is named
        # CORGIS often uses 'Data.Date.Time' or 'Date'
        date_col = [c for c in df.columns if 'Date' in c][0]
        lat_col = [c for c in df.columns if 'Latitude' in c][0]
        lon_col = [c for c in df.columns if 'Longitude' in c][0]
        
        df = df.rename(columns={date_col: 'time', lat_col: 'lat', lon_col: 'lon'})
        df['time'] = pd.to_datetime(df['time'], errors='coerce', utc=True)
        return df.dropna(subset=['lat', 'lon', 'time'])
    except Exception as e:
        st.error(f"UAP Load Error: Check mirror status. ({e})")
        return pd.DataFrame()

# 2. Stable Seismic Feed (GeoJSON Summary)
def get_seismic_data():
    # Using the pre-generated 'Past Day' Summary Feed for maximum stability
    url = "https://earthquake.usgs.gov"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200: return pd.DataFrame()
        data = resp.json()
        points = []
        for f in data['features']:
            coords = f['geometry']['coordinates']
            points.append({
                'lat': coords[1], 'lon': coords[0], 
                'mag': f['properties']['mag'], 'place': f['properties']['place'],
                'time': pd.to_datetime(f['properties']['time'], unit='ms', utc=True)
            })
        return pd.DataFrame(points)
    except: return pd.DataFrame()

# 3. Main Dashboard
st.title("Guardian Predictor: Robust Stream Link")
uap_df = get_uap_data()
live_df = get_seismic_data()

if not uap_df.empty and not live_df.empty:
    st.success("Streams Synchronized.")
    st.map(pd.concat([uap_df.head(100), live_df])) # Simplified test map
else:
    st.warning("One or more planetary data streams are still offline.")
