import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

from core.cluster_orchestrator import ClusterOrchestrator
from research.autonomous_discovery import AutonomousDiscoveryEngine
from ingestion.usgs_stream import fetch_usgs_earthquakes

# -----------------------------------
# Configuration
# -----------------------------------

API_URL = "http://localhost:8000"

cluster = ClusterOrchestrator()
discovery = AutonomousDiscoveryEngine()

st.set_page_config(
    page_title="IHRAS Scientific Research Dashboard",
    layout="wide"
)

st.title("IHRAS – Integrated Hazard Research & Autonomous Science")

# -----------------------------------
# Sidebar Controls
# -----------------------------------

st.sidebar.header("Research Controls")

run_cycle = st.sidebar.button("Run Autonomous Research Cycle")
submit_test = st.sidebar.button("Submit Test Cluster Job")

# -----------------------------------
# Autonomous Discovery
# -----------------------------------

if run_cycle:

    jobs = discovery.run_cycle(10)

    st.success(f"Launched {len(jobs)} autonomous experiments")

# -----------------------------------
# Cluster Job Submission
# -----------------------------------

if submit_test:

    def sample_experiment(x=3, y=4):
        return {"result": x**2 + y**2}

    job_id = cluster.submit_job(sample_experiment)

    st.success(f"Cluster Job Submitted: {job_id}")

# -----------------------------------
# USGS Data Section
# -----------------------------------

st.header("Global Seismic Activity")

try:

    df = fetch_usgs_earthquakes()

    df = df.dropna(subset=["longitude", "latitude", "magnitude"])

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            text=df["place"],
            mode="markers",
            marker=dict(
                size=df["magnitude"] * 3,
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

except Exception as e:

    st.warning("USGS data currently unavailable")
    st.text(str(e))

# -----------------------------------
# Artifact Ledger Viewer
# -----------------------------------

st.header("Research Artifact Ledger")

try:

    r = requests.get(f"{API_URL}/artifacts")

    if r.status_code == 200:

        artifacts = r.json()

        if artifacts:

            st.write("Stored Research Artifacts")

            for a in artifacts:

                st.code(a)

        else:

            st.info("No artifacts recorded yet")

except:

    st.info("Artifact server not running")

# -----------------------------------
# Discovery Metrics
# -----------------------------------

st.header("System Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Experiments Run", "Dynamic")
col3.metric("Artifacts Stored", "Dynamic")

# -----------------------------------
# Research Console
# -----------------------------------

st.header("Scientific Experiment Console")

param_x = st.number_input("Parameter X", value=1.0)
param_y = st.number_input("Parameter Y", value=2.0)

if st.button("Run Custom Experiment"):

    def custom_experiment(x, y):

        return {
            "experiment": "custom",
            "parameters": {"x": x, "y": y},
            "result": x**2 + y**2
        }

    job_id = cluster.submit_job(custom_experiment, param_x, param_y)

    st.success(f"Experiment launched: {job_id}")

# -----------------------------------
# Footer
# -----------------------------------

st.markdown("---")
st.caption("IHRAS Autonomous Scientific Computing Platform")
