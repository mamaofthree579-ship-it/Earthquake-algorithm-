"""
Streamlit prototype for IHRAS v1.0.
- Shows USGS earthquakes (map + table)
- Attempts to fetch NOAA SWPC solar-wind sample
- Provides a demo harmonics FFT panel
"""
import streamlit as st
from ingest.usgs import fetch_usgs_week
from ingest.jpl import get_example_ephemeris
from harmonics.processor import demo_harmonics_plot
import pandas as pd

st.set_page_config(layout="wide", page_title="IHRAS v1.0 Prototype")
st.title("IHRAS v1.0 — Integrated Harmonic Risk & Awareness System (Prototype)")

st.sidebar.header("Data sources")
use_usgs = st.sidebar.checkbox("Include USGS earthquake feed (past 7 days)", True)
use_ephem = st.sidebar.checkbox("Include sample ephemeris (JPL HORIZONS)", False)

col1, col2 = st.columns([2, 1])

if use_usgs:
    with col1:
        st.subheader("Recent Earthquakes (USGS — past 7 days)")
        try:
            df = fetch_usgs_week()
            if not df.empty:
                st.map(df.rename(columns={"latitude": "lat", "longitude": "lon"})[["lat", "lon"]])
                st.dataframe(df.sort_values("magnitude", ascending=False).head(100))
            else:
                st.info("No earthquake records returned.")
        except Exception as e:
            st.error(f"Failed to fetch USGS feed: {e}")

with col2:
    st.subheader("Ephemeris (sample)")
    if use_ephem:
        try:
            txt = get_example_ephemeris()
            st.code(txt[:2000])
        except Exception as e:
            st.error(f"Ephemeris fetch error: {e}")
    else:
        st.write("Enable `Include sample ephemeris` in the sidebar to fetch a short JPL example.")

st.markdown("---")
st.subheader("Signal processing & harmonics demo")
st.write("This demo synthesizes a low-frequency 'tectonic' signal and a high-frequency 'solar' signal and shows FFT peaks.")
demo_harmonics_plot()
st.caption("Demo FFT — not a real predictive output. Replace with real harmonics pipeline.")
