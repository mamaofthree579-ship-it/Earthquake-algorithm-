import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

from core.cluster_orchestrator import ClusterOrchestrator
from research.autonomous_discovery import AutonomousDiscoveryEngine
from ingestion.usgs_stream import fetch_usgs_earthquakes


# ----------------------------------------------------
# Page Setup
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Dashboard",
    layout="wide"
)

st.title("🌍 IHRAS Integrated Hazard Research Platform")


# ----------------------------------------------------
# Initialize Core Systems
# ----------------------------------------------------

if "cluster" not in st.session_state:
    st.session_state.cluster = ClusterOrchestrator()

if "discovery" not in st.session_state:
    st.session_state.discovery = AutonomousDiscoveryEngine()

cluster = st.session_state.cluster
discovery = st.session_state.discovery


# ----------------------------------------------------
# Sidebar Controls
# ----------------------------------------------------

st.sidebar.header("Autonomous Research Controls")

if st.sidebar.button("Run Discovery Cycle"):
    jobs = discovery.run_cycle(10)
    st.sidebar.success(f"Launched {len(jobs)} autonomous experiments")


# ----------------------------------------------------
# Global Seismic Visualization
# ----------------------------------------------------

st.header("🌎 Global Seismic Activity Map")

try:
    df = fetch_usgs_earthquakes()

    if df is not None and not df.empty:

        df = df.dropna(subset=["longitude", "latitude", "magnitude"])

        # Safety clamp magnitude
        df["magnitude"] = df["magnitude"].apply(
            lambda x: max(float(x), 0.1)
        )

        marker_size = df["magnitude"] * 3

        fig = go.Figure()

        fig.add_trace(
            go.Scattergeo(
                lon=df["longitude"],
                lat=df["latitude"],
                text=df["place"],
                mode="markers",
                marker=dict(
                    size=marker_size.tolist(),
                    opacity=0.7
                )
            )
        )

        fig.update_layout(
            geo=dict(
                projection_type="natural earth",
                showland=True
            ),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Seismic dataset currently empty.")

except Exception as e:
    st.warning("Hazard feed unavailable — displaying safe dashboard state.")
    st.text(str(e))


# ----------------------------------------------------
# Experiment Console
# ----------------------------------------------------

st.header("🧪 Scientific Experiment Console")

param_x = st.number_input("Parameter X", value=1.0)
param_y = st.number_input("Parameter Y", value=2.0)


if st.button("Run Test Experiment"):

    def experiment(x, y):
        return {
            "experiment": "test_model",
            "parameters": {"x": x, "y": y},
            "result": float(x*x + y*y)
        }

    job_id = cluster.submit_job(
        experiment,
        param_x,
        param_y
    )

    st.success(f"Experiment job launched → {job_id}")


# ----------------------------------------------------
# Artifact Ledger Viewer
# ----------------------------------------------------

st.header("📚 Research Artifact Ledger")

try:
    artifacts = cluster.ledger.list_artifacts()

    if artifacts:
        st.write("Stored Experiment Artifacts")

        for a in artifacts:
            st.code(a)

    else:
        st.info("No research artifacts recorded yet.")

except Exception:
    st.info("Ledger subsystem offline.")


# ----------------------------------------------------
# System Metrics Panel
# ----------------------------------------------------

st.header("📊 Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Running Experiments", "Dynamic")
col3.metric("Artifact Records", "Dynamic")


st.markdown("---")
st.caption("IHRAS Autonomous Scientific Research Platform")
