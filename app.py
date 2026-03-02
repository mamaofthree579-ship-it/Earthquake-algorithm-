import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import time

from models.spherical_pde import run_simulation
from models.monte_carlo import run_ensemble

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(layout="wide")
st.title("🌍 IHRAS v4.0 — Planetary Harmonic Research Dashboard")

# -------------------------------------------------
# DATA SOURCES
# -------------------------------------------------

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
KPINDEX_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
ENSO_URL = "https://psl.noaa.gov/data/correlation/oni.data"

# -------------------------------------------------
# CACHE FUNCTIONS
# -------------------------------------------------

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

        if df.empty:
            return df

        # ----- HARD CLEANING -----
        df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=["mag", "lat", "lon"])

        df = df[df["mag"] > 0]
        df = df[(df["lat"].between(-90, 90)) &
                (df["lon"].between(-180, 180))]

        return df

    except Exception as e:
        st.error(f"Earthquake feed error: {e}")
        return pd.DataFrame()

class UltimateIHRASSolver:

    def __init__(self,
                 diffusion=0.2,
                 damping=0.3,
                 fracture=0.02):

        self.D = diffusion
        self.lambda_d = damping
        self.kappa = fracture

        self.field = np.random.normal(0,0.01,(90,180))

    def forcing(self, t):

        solar = np.cos(2*np.pi*t/27)
        lunar = 0.5*np.cos(2*np.pi*t/29.5)

        return solar + lunar

    def step(self, dt=0.01):

        lap = np.gradient(self.field)[0]

        nonlinear = self.kappa * self.field**3
        noise = 0.05 * np.random.randn(*self.field.shape)

        self.field += dt * (
            self.D * lap
            - self.lambda_d * self.field
            + nonlinear
            + self.forcing(time.time())
            + noise
        )

        return self.field
        
# -------------------------------------------------
# ENVIRONMENTAL INDICES
# -------------------------------------------------

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
        return float(latest[1:].mean())
    except:
        return 0.0

# -------------------------------------------------
# CELESTIAL HARMONIC FORCE
# -------------------------------------------------

def celestial_forcing():

    t = time.time() / 86400.0

    solar_rot = np.cos(2*np.pi*t/27)
    lunar_cycle = 0.5*np.cos(2*np.pi*t/29.5)
    precession = 0.1*np.cos(2*np.pi*t/(26000*365))

    return solar_rot + lunar_cycle + precession

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = fetch_earthquakes()
kp = fetch_kp_index()
enso = fetch_enso_index()
celestial = celestial_forcing()

# -------------------------------------------------
# SIDEBAR PANEL
# -------------------------------------------------

st.sidebar.header("🌐 Global Monitoring")

st.sidebar.metric("ENSO Index", round(enso, 3))
st.sidebar.metric("Kp Index", round(kp, 3))
st.sidebar.metric("Celestial Harmonic", round(celestial, 3))

# -------------------------------------------------
# EARTHQUAKE MAP VISUALIZATION
# -------------------------------------------------

st.header("🌎 Live Earthquake Map")

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
# SPHERICAL PDE STRESS SIMULATION
# -------------------------------------------------

st.header("🌐 Spherical Stress Diffusion Simulation")

stress = run_simulation(
    celestial_amp=abs(celestial)+0.5,
    noise_amp=0.05
)

fig2 = go.Figure(
    data=go.Heatmap(
        z=stress,
        colorscale="Turbo"
    )
)

fig2.update_layout(height=450)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# MONTE CARLO PROBABILITY CONE
# -------------------------------------------------

st.header("📡 Monte Carlo Probability Cone")

prob_map = run_ensemble(runs=15)

fig3 = go.Figure(
    data=go.Heatmap(
        z=prob_map,
        colorscale="Inferno"
    )
)

fig3.update_layout(height=450)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------
# FRACTURE BIFURCATION WARNING
# -------------------------------------------------

st.header("⚠ System Stability Assessment")

max_stress = float(np.max(np.abs(stress)))

if max_stress > 2.0:
    st.warning("⚠ Nonlinear Fracture Bifurcation Detected")
elif max_stress > 1.2:
    st.info("Moderate Stress Accumulation")
else:
    st.success("System within Stable Basin")

risk_index = (np.mean(stress) +
              abs(celestial) +
              kp +
              abs(enso)) / 3

st.subheader(f"🌡 Composite Risk Index: {risk_index:.3f}")

