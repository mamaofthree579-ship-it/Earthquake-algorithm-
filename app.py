# app.py

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ingestion.usgs_stream import fetch_usgs_earthquakes

from core.cluster_orchestrator import ClusterOrchestrator
from core.mesh_federation import MeshFederation

from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI
from research.reproducibility_engine import ReproducibilityEngine


# ---------------------------------------------------------
# System Initialization
# ---------------------------------------------------------

cluster = ClusterOrchestrator()
federation = MeshFederation()

harmonic_engine = PlanetaryHarmonicPredictionEngine()
compression_solver = SpacetimeCompressionSolver()
tensor_engine = HarmonicTensorDiscovery()

discovery_ai = AutonomousDiscoveryAI()
repro_engine = ReproducibilityEngine()


# ---------------------------------------------------------
# Streamlit Page
# ---------------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Planetary Research Platform")


# ---------------------------------------------------------
# Fetch Earthquake Data
# ---------------------------------------------------------

df = fetch_usgs_earthquakes()

if df is None or df.empty:
    st.warning("USGS data currently unavailable")
    df = pd.DataFrame(columns=["latitude", "longitude", "magnitude"])

# clean data
df = df.dropna(subset=["latitude", "longitude", "magnitude"])

# ensure numeric
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")

# safe marker sizes
df["marker_size"] = df["magnitude"].clip(lower=0) * 3


# ---------------------------------------------------------
# Plot Earthquake Map
# ---------------------------------------------------------

fig = go.Figure()

if not df.empty:

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            mode="markers",
            marker=dict(
                size=df["marker_size"],
                opacity=0.7
            ),
            text=df["magnitude"]
        )
    )

fig.update_layout(
    geo=dict(
        projection_type="natural earth"
    ),
    title="Global Seismic Activity"
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# Submit Research Job
# ---------------------------------------------------------

st.subheader("Submit Scientific Experiment")

if st.button("Run Experiment"):

    payload = {
        "experiment": "harmonic_analysis"
    }

    result = cluster.submit_job(payload)

    st.success(f"Job submitted: {result}")


# ---------------------------------------------------------
# Harmonic Analysis
# ---------------------------------------------------------

st.subheader("Planetary Harmonic Prediction")

if not df.empty:

    harmonic_result = harmonic_engine.analyze(df)

    st.write(harmonic_result)


# ---------------------------------------------------------
# Spacetime Compression Solver
# ---------------------------------------------------------

st.subheader("Spacetime Compression Field")

if not df.empty:

    compression_result = compression_solver.solve(df)

    st.write(compression_result)


# ---------------------------------------------------------
# Harmonic Tensor Discovery
# ---------------------------------------------------------

st.subheader("Harmonic Tensor Discovery")

if not df.empty:

    tensor_result = tensor_engine.discover(df)

    st.write(tensor_result)


# ---------------------------------------------------------
# Autonomous Discovery AI
# ---------------------------------------------------------

st.subheader("Autonomous Discovery AI")

if not df.empty:

    discoveries = discovery_ai.generate_hypotheses(df)

    st.write(discoveries)


# ---------------------------------------------------------
# Reproducibility Engine
# ---------------------------------------------------------

st.subheader("Reproducibility Verification")

experiment_data = {"sample": "test"}

hash_id = repro_engine.hash_experiment(experiment_data)

st.write("Experiment Hash:", hash_id)


# ---------------------------------------------------------
# Federation Mesh
# ---------------------------------------------------------

st.subheader("Scientific Mesh Federation")

if st.button("Register Local Node"):

    node_id = federation.register_node(
        "local_node",
        "http://localhost:8000"
    )

    st.success(f"Node Registered: {node_id}")

nodes = federation.list_nodes()

st.write("Federation Nodes:", nodes)
