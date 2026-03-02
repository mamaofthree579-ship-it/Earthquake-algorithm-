import streamlit as st
import plotly.graph_objects as go

from services.data_ingestion import fetch_usgs_earthquakes
from physics.stress_solver import HarmonicStressSolver

st.set_page_config(layout="wide")

st.title("🌍 IHRAS Production Research Dashboard")

# Cache data
@st.cache_data(ttl=300)
def load_data():
    return fetch_usgs_earthquakes()

df = load_data()

solver = HarmonicStressSolver()
stress = solver.step()

# Map Visualization
fig = go.Figure()

if not df.empty:

    fig.add_trace(go.Scattergeo(
        lon=df["longitude"],
        lat=df["latitude"],
        text=df["place"],
        marker=dict(
            size=df["magnitude"] * 2,
            color=df["magnitude"],
            colorscale="Viridis",
            showscale=True
        )
    ))

fig.update_geos(projection_type="natural earth")

st.plotly_chart(fig, use_container_width=True)

# Stability Metric
stability_index = 1 / (1 + np.var(stress))

st.metric(
    "System Stability Index",
    f"{stability_index:.4f}"
)
