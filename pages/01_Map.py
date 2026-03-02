import streamlit as st
from ingest.usgs import fetch_usgs_week
import pandas as pd

st.title("Map — Recent Earthquakes & Observations")

st.write("This page visualizes recent USGS earthquakes from the 7-day feed.")

try:
    df = fetch_usgs_week()
   st.map(df[["latitude", "longitude"]])
   st.success(f"Loaded {len(df)} quakes")
    if not df.empty:
        map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon", "magnitude", "place", "time_utc"]].dropna()
        st.map(map_df[["lat","lon"]])
        st.dataframe(map_df.sort_values("magnitude", ascending=False).head(200))
    else:
        st.info("No earthquake data available")
except Exception as e:
    st.error(f"Failed to load USGS data: {e}")

# share with Predictions tab as ingestion tab
st.session_state["quakes"] = df
