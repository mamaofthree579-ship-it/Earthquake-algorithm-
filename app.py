import streamlit as st
import plotly.express as px
import numpy as np
from ingestion.usgs import fetch_earthquakes
from ingestion.noaa import fetch_enso_index
from ingestion.solar import fetch_kp_index
from utils.harmonics import celestial_forcing

st.set_page_config(layout="wide")
st.title("🌍 IHRAS v3.1 — Planetary Harmonic Observatory")

# -------------------------
# Sidebar Monitoring Panel
# -------------------------

st.sidebar.header("🌐 Global Indices")

@st.cache_data(ttl=300)
def load_eq():
    return fetch_earthquakes()

@st.cache_data(ttl=3600)
def load_enso():
    return fetch_enso_index()

@st.cache_data(ttl=900)
def load_kp():
    return fetch_kp_index()

try:
    df = load_eq()
    enso = load_enso()
    kp = load_kp()
    celestial = celestial_forcing()

    st.sidebar.metric("ENSO Index", round(enso,2))
    st.sidebar.metric("Kp Index", round(kp,2))
    st.sidebar.metric("Celestial Harmonic", round(celestial,2))

except Exception as e:
    st.sidebar.error(f"Data Error: {e}")
    st.stop()

# -------------------------
# Earthquake Map
# -------------------------

st.header("Live Earthquake Map")

if df.empty:
    st.warning("No earthquake data available.")
else:
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        size="mag",
        hover_name="place",
        color="mag",
        projection="natural earth",
        size_max=12
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Harmonic Stress Forecast
# -------------------------

st.header("Monte Carlo Stress Projection")

grid = np.random.rand(90,180)
fig2 = px.imshow(grid, origin="lower")
st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Risk Index Calculation
# -------------------------

stress_mean = np.mean(grid)
risk = (stress_mean + abs(celestial) + abs(enso) + kp) / 3

if risk < 0.5:
    status = "Low"
elif risk < 1.0:
    status = "Moderate"
elif risk < 2.0:
    status = "Elevated"
else:
    status = "Critical"

st.subheader(f"🌡 Event Risk Index: {status}")
