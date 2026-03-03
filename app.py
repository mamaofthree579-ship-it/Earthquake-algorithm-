import streamlit as st
import plotly.graph_objects as go
import numpy as np

from ingestion.usgs_stream import fetch_usgs_stream
from physics.solver_kernel import HarmonicSolverKernel
from analytics.stability_metrics import compute_stability_index

st.set_page_config(layout="wide")

st.title("🌍 IHRAS Laboratory Edition")

# --------------------------
# Data Layer
# --------------------------

df = fetch_usgs_stream()

if df.empty:
    st.warning("No streaming data available")

else:
    df["magnitude"] = df["magnitude"].astype(float)
    df["marker_size"] = np.clip(df["magnitude"] * 2, 2, 20)

# --------------------------
# Physics Simulation Kernel
# --------------------------

solver = HarmonicSolverKernel()
stress_field = solver.step()

# --------------------------
# Visualization
# --------------------------

fig = go.Figure()

if not df.empty:

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

fig.update_geos(
    projection_type="natural earth"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Stability Metric
# --------------------------

stability = compute_stability_index(
    df["magnitude"].tolist() if not df.empty else []
)

st.metric(
    "System Stability Index",
    f"{stability:.4f}"
)
