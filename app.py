import streamlit as st
import numpy as np
import plotly.express as px
from ingestion.usgs import fetch_earthquakes
from models.spherical_mesh import generate_spherical_grid

st.set_page_config(layout="wide")
st.title("🌍 IHRAS v3.0 — Integrated Harmonic Risk & Awareness System")

st.header("Live Earthquake Feed")

df = fetch_earthquakes()

# ✅ CLEAN DATA
df = df.dropna(subset=["lat", "lon", "mag"])
df = df[df["mag"] > 0]

if df.empty:
    st.warning("No valid earthquake data available.")
else:
    df["mag"] = df["mag"].astype(float)

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        size="mag",
        hover_name="place",
        projection="natural earth",
        size_max=12
    )

    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="rgb(243,243,243)",
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
# Harmonic Forecast Panel
st.header("Monte Carlo Harmonic Stress Forecast")

stress = np.random.rand(90,180)
lat, lon = generate_spherical_grid()

fig2 = px.imshow(stress, origin="lower")
st.plotly_chart(fig2, use_container_width=True)
