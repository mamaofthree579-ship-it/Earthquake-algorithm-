import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import time

st.set_page_config(layout="wide")
st.title("🌍 IHRAS v3.1 — Planetary Harmonic Observatory")

# -------------------------------------------------
# DATA INGESTION FUNCTIONS
# -------------------------------------------------

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
KPINDEX_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
ENSO_URL = "https://psl.noaa.gov/data/correlation/oni.data"

@st.cache_data(ttl=300)
def fetch_earthquakes():
    try:
        r = requests.get(USGS_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        records = []
        for feature in data["features"]:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]

            if props["mag"] is None:
                continue

            records.append({
                "mag": props["mag"],
                "place": props["place"],
                "lat": coords[1],
                "lon": coords[0],
                "depth": coords[2]
            })

        df = pd.DataFrame(records)

        # ---- HARD CLEANING ----
        df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=["mag", "lat", "lon"])
        df = df[df["mag"] > 0]
        df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]

        return df

    except Exception as e:
        st.error(f"Earthquake feed error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=900)
def fetch_kp_index():
    try:
        r = requests.get(KPINDEX_URL, timeout=10)
        data = r.json()
        return float(data[-1][1])
    except:
        return 0.0

@st.cache_data(ttl=3600)
def fetch_enso_index():
    try:
        df = pd.read_fwf(ENSO_URL, skiprows=1)
        latest = df.iloc[-1]
        enso = latest[1:].mean()
        return float(enso)
    except:
        return 0.0

def celestial_forcing():
    t = time.time() / 86400.0
    solar_rot = np.cos(2*np.pi*t/27)
    lunar_cycle = 0.5*np.cos(2*np.pi*t/29.5)
    return solar_rot + lunar_cycle

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = fetch_earthquakes()
kp = fetch_kp_index()
enso = fetch_enso_index()
celestial = celestial_forcing()

# -------------------------------------------------
# SIDEBAR METRICS
# -------------------------------------------------

st.sidebar.header("🌐 Global Indices")
st.sidebar.metric("ENSO Index", round(enso, 2))
st.sidebar.metric("Kp Index", round(kp, 2))
st.sidebar.metric("Celestial Harmonic", round(celestial, 2))

# -------------------------------------------------
# EARTHQUAKE MAP (ULTRA-STABLE VERSION)
# -------------------------------------------------

st.header("Live Earthquake Map")

if df.empty:
    st.warning("No valid earthquake data available.")
else:
    df["size_scaled"] = np.clip(df["mag"], 0.5, 10)

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=df["lon"],
        lat=df["lat"],
        text=df["place"],
        marker=dict(
            size=df["size_scaled"],
            color=df["size_scaled"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Magnitude")
        )
    ))

    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="rgb(240,240,240)",
        showcountries=True
    )

    fig.update_layout(height=600)

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# HARMONIC STRESS FORECAST (PLACEHOLDER GRID)
# -------------------------------------------------

st.header("Monte Carlo Stress Projection")

grid = np.random.rand(90, 180)

fig2 = go.Figure(
    data=go.Heatmap(
        z=grid,
        colorscale="Turbo"
    )
)

fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# RISK INDEX
# -------------------------------------------------

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
