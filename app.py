import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Ingestion
from ingestion.usgs_stream import fetch_usgs_earthquakes

# Core Runtime
from core.cluster_orchestrator import ClusterOrchestrator
from core.institutional_runtime_os import InstitutionalScientificRuntimeOS

# Research Engines
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI


# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Scientific Simulation Dashboard")


# ----------------------------------------------------
# Runtime Initialization
# ----------------------------------------------------

def init_engine(key, cls):
    if key not in st.session_state:
        st.session_state[key] = cls()
    return st.session_state[key]


cluster = init_engine("cluster", ClusterOrchestrator)
runtime_os = init_engine("runtime_os", InstitutionalScientificRuntimeOS)

harmonic_engine = init_engine(
    "harmonic_engine",
    PlanetaryHarmonicPredictionEngine
)

solver = init_engine(
    "solver",
    SpacetimeCompressionSolver
)

tensor_engine = init_engine(
    "tensor_engine",
    HarmonicTensorDiscovery
)

discovery_ai = init_engine(
    "discovery_ai",
    AutonomousDiscoveryAI
)


# ----------------------------------------------------
# Data Ingestion
# ----------------------------------------------------

st.header("🌎 Global Seismic Activity")

df = None

try:
    df = fetch_usgs_earthquakes()

    if df is None or df.empty:
        st.warning("USGS data currently unavailable.")
        df = None

except Exception:
    st.warning("Ingestion subsystem offline.")
    df = None


# ----------------------------------------------------
# Visualization Layer
# ----------------------------------------------------

if df is not None:

    df = df.dropna(subset=["longitude", "latitude", "magnitude"])

    df["magnitude"] = df["magnitude"].abs().clip(lower=0.1)

    marker_size = df["magnitude"] * 3

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            mode="markers",
            marker=dict(
                size=marker_size,
                opacity=0.7
            )
        )
    )

    fig.update_layout(
        geo=dict(projection_type="natural earth"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------
# Harmonic Simulation
# ----------------------------------------------------

st.header("🌌 Harmonic Prediction Simulation")

t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):

    score = harmonic_engine.analyze(
        df if df is not None else st.session_state.get("last_df", None)
    )

    st.json(score)


# ----------------------------------------------------
# Compression Solver
# ----------------------------------------------------

st.header("🌀 Compression Field Solver")

if df is not None and st.button("Run Compression Simulation"):

    result = solver.compute(df)

    st.json(result)


# ----------------------------------------------------
# Tensor Discovery
# ----------------------------------------------------

st.header("🔬 Harmonic Tensor Discovery")

if df is not None and st.button("Run Tensor Discovery"):

    result = tensor_engine.discover(df)

    st.json(result)


# ----------------------------------------------------
# Discovery AI
# ----------------------------------------------------

st.header("🤖 Autonomous Discovery AI")

if df is not None and st.button("Run Discovery Analysis"):

    result = discovery_ai.analyze(df)

    st.json(result)


# ----------------------------------------------------
# Institutional Runtime OS Panel
# ----------------------------------------------------

st.header("🏛 Institutional Scientific Runtime OS")

if st.button("Run Institutional Research Task"):

    def scientific_task():
        return {"status": "runtime_task_completed"}

    job_id = runtime_os.submit_scientific_job(
        scientific_task
    )

    st.success(f"Scientific Job Submitted: {job_id}")


# ----------------------------------------------------
# Cluster Runtime Panel
# ----------------------------------------------------

st.header("📡 Research Cluster Runtime")

if st.button("Submit Cluster Research Task"):

    payload = {
        "task": "simulation_analysis",
        "dataset_rows": 0 if df is None else len(df)
    }

    job_id = cluster.submit_job(payload)

    st.success(f"Cluster job submitted: {job_id}")


# ----------------------------------------------------
# Artifact Ledger
# ----------------------------------------------------

st.header("📚 Research Artifact Ledger")

try:
    artifacts = cluster.ledger.list_artifacts()

    if artifacts:
        for artifact in artifacts:
            st.code(artifact)
    else:
        st.info("No research artifacts recorded.")

except Exception:
    st.info("Ledger subsystem unavailable.")


# ----------------------------------------------------
# Platform Status
# ----------------------------------------------------

st.markdown("---")

st.subheader("Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Active")
col3.metric("Artifact Records", "Dynamic")

st.caption("IHRAS Research Simulation Prototype")
