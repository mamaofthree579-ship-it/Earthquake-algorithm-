import streamlit as st
import plotly.graph_objects as go

from services.data_ingestion import fetch_usgs_earthquakes
from physics.stress_solver import HarmonicStressSolver

st.set_page_config(layout="wide")

st.title("🌍 IHRAS Production Research Dashboard")

# -------------------------------
# Safe Data Cleaning (IMPORTANT)
# -------------------------------

df = df.dropna(subset=["longitude", "latitude", "magnitude"])

df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")
df = df[df["magnitude"] > 0]

# Clamp magnitude for Plotly safety
df["marker_size"] = np.clip(df["magnitude"] * 2, 2, 20)

# -------------------------------
# Plotly Map Visualization
# -------------------------------

fig = go.Figure()

if not df.empty:

    fig.add_trace(go.Scattergeo(
        lon=df["longitude"],
        lat=df["latitude"],
        text=df["place"] if "place" in df.columns else "",
        mode="markers",
        marker=dict(
            size=df["marker_size"].tolist(),  # ← CRITICAL FIX
            color=df["magnitude"].tolist(),
            colorscale="Viridis",
            showscale=True
        )
    ))

fig.update_geos(
    projection_type="natural earth"
)

st.plotly_chart(fig, use_container_width=True)

# Stability Metric
stability_index = 1 / (1 + np.var(stress))

st.metric(
    "System Stability Index",
    f"{stability_index:.4f}"
)
