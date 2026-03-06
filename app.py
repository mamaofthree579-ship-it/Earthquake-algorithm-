# app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Core infrastructure
from core.cluster_orchestrator import ClusterOrchestrator
from core.reproducibility_engine import ReproducibilityEngine

# Ingestion
from ingestion.usgs_stream import fetch_usgs_earthquakes

# Research engines
from research.harmonic_prediction_engine import HarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI


# -----------------------------
# Initialize Engines
# -----------------------------

cluster = ClusterOrchestrator()
repro_engine = ReproducibilityEngine()

harmonic_engine = HarmonicPredictionEngine()
compression_solver = SpacetimeCompressionSolver()
tensor_engine = HarmonicTensorDiscovery()
discovery_ai = AutonomousDiscoveryAI()


# -----------------------------
# UI
# -----------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Planetary Harmonic Research System")


# -----------------------------
# Fetch Earthquake Data
# -----------------------------

try:

    data = fetch_usgs_earthquakes()

    if data is None or len(data) == 0:
        st.warning("USGS data currently unavailable.")
        df = pd.DataFrame()

    else:
        df = pd.DataFrame(data)

        df = df.dropna(subset=["longitude", "latitude", "magnitude"])

except Exception as e:

    st.warning("USGS data currently unavailable.")
    df = pd.DataFrame()


# -----------------------------
# Visualization
# -----------------------------

if not df.empty:

    # Ensure marker size always positive
    marker_sizes = (df["magnitude"].abs() + 0.1) * 4

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            text=df["magnitude"],
            mode="markers",
            marker=dict(
                size=marker_sizes,
                opacity=0.7
            )
        )
    )

    fig.update_layout(
        title="Global Seismic Activity",
        geo=dict(
            showland=True
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Research Engines
# -----------------------------

if not df.empty:

    st.subheader("Scientific Analysis Engines")

    # Harmonic Prediction
    harmonic_results = harmonic_engine.analyze(df)

    # Spacetime Compression
    compression_results = compression_solver.compute(df)

    # Harmonic Tensor Discovery
    tensor_results = tensor_engine.discover(df)

    # Autonomous Discovery
    discovery_results = discovery_ai.analyze(df)


    st.write("Harmonic Prediction Results")
    st.json(harmonic_results)

    st.write("Spacetime Compression Results")
    st.json(compression_results)

    st.write("Harmonic Tensor Structures")
    st.json(tensor_results)

    st.write("Autonomous Discovery AI")
    st.json(discovery_results)


# -----------------------------
# Reproducibility Record
# -----------------------------

payload = {
    "rows": len(df)
}

record = repro_engine.create_reproducibility_record(payload)

st.subheader("Reproducibility Record")

st.json(record)


# -----------------------------
# Cluster Job Submission
# -----------------------------

if st.button("Submit Research Job to Cluster"):

    job = {
        "task": "planetary_analysis",
        "data_rows": len(df)
    }

    job_id = cluster.submit_job(job)

    st.success(f"Job submitted to research cluster: {job_id}")


# -----------------------------
# Footer
# -----------------------------

st.markdown("---")

st.caption("IHRAS — Integrated Harmonic Research and Analysis System")
