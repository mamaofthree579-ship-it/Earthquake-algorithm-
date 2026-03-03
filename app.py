import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests

# ------------------------------
# Configuration
# ------------------------------

st.set_page_config(layout="wide")
st.title("🌍 IHRAS Open Science Research Platform")

# ------------------------------
# Data Ingestion Layer
# ------------------------------

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_stream():

    try:
        response = requests.get(USGS_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        records = []

        for feature in data.get("features", []):

            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            if len(coords) < 2:
                continue

            records.append({
                "longitude": coords[0],
                "latitude": coords[1],
                "magnitude": props.get("mag", 0)
            })

        return pd.DataFrame(records)

    except Exception:
        return pd.DataFrame()

# ------------------------------
# Research Kernel Simulation
# ------------------------------

def research_kernel_simulation(grid=(180,360)):

    field = np.random.normal(0,0.001,grid)

    laplacian = (
        np.roll(field,1,0)+
        np.roll(field,-1,0)+
        np.roll(field,1,1)+
        np.roll(field,-1,1)-
        4*field
    )

    field += 0.01*(0.15*laplacian - 0.25*field)

    return field

# ------------------------------
# Visualization Layer
# ------------------------------

df = fetch_stream()

if not df.empty:

    df["magnitude"] = df["magnitude"].fillna(0)
    df["marker_size"] = np.clip(df["magnitude"]*2,2,20)

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon=df["longitude"].tolist(),
        lat=df["latitude"].tolist(),
        mode="markers",
        marker=dict(
            size=df["marker_size"].tolist(),
            color=df["magnitude"].tolist(),
            colorscale="Viridis"
        )
    ))

    fig.update_geos(projection_type="natural earth")

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No streaming research data available")

# ------------------------------
# Research Metrics Dashboard
# ------------------------------

field = research_kernel_simulation()

entropy_proxy = -np.mean(
    field*np.log(np.abs(field)+1e-8)
)

st.metric(
    "Research Entropy Proxy",
    f"{entropy_proxy:.6f}"
)
