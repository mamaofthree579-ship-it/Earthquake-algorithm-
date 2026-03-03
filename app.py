import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from ingestion.usgs_stream import fetch_usgs_stream
from core.solver_kernel import SolverKernel
from visualization.maps import render_global_map
from visualization.gauges import render_gauge

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

# -------------------------------
# Sidebar Navigation
# -------------------------------

st.sidebar.title("🌍 IHRAS Research Control")

mode = st.sidebar.selectbox(
    "Research Mode",
    [
        "Dashboard",
        "Simulation Kernel",
        "Federation Metrics",
        "Data Exploration"
    ]
)

st.sidebar.markdown("---")

# -------------------------------
# Load Data
# -------------------------------

df = fetch_usgs_stream()

# -------------------------------
# Dashboard Mode
# -------------------------------

if mode == "Dashboard":

    st.title("🌌 Open Science Research Dashboard")

    col1, col2 = st.columns(2)

    # Global Map Visualization
    with col1:

        st.subheader("🗺️ Global Event Distribution")

        if not df.empty:

            fig = render_global_map(
                df["longitude"].tolist(),
                df["latitude"].tolist(),
                df["magnitude"].tolist()
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No research stream data available")

    # Cluster Health Metric
    with col2:

        st.subheader("🔬 Research Kernel Stability Proxy")

        kernel = SolverKernel()

        field = kernel.step()

        entropy_proxy = -np.mean(
            field * np.log(np.abs(field) + 1e-8)
        )

        fig = render_gauge(
            entropy_proxy,
            title="Entropy Activity Index"
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Simulation Kernel Mode
# -------------------------------

elif mode == "Simulation Kernel":

    st.title("🧠 Scientific Simulation Kernel")

    kernel = SolverKernel()

    if st.button("Run Kernel Step"):

        field = kernel.step()

        st.success("Kernel simulation executed")

        fig = go.Figure(
            go.Heatmap(
                z=field,
                colorscale="Viridis"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Federation Metrics Mode
# -------------------------------

elif mode == "Federation Metrics":

    st.title("☁️ Cluster Federation Metrics")

    node_scores = {
        "Node-A": np.random.rand(),
        "Node-B": np.random.rand(),
        "Node-C": np.random.rand()
    }

    fig = go.Figure(go.Bar(
        x=list(node_scores.keys()),
        y=list(node_scores.values())
    ))

    fig.update_layout(
        title="Scientific Cluster Health Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Data Exploration Mode
# -------------------------------

elif mode == "Data Exploration":

    st.title("📊 Research Dataset Explorer")

    st.dataframe(df)
