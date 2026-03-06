import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Ingestion
from ingestion.usgs_stream import fetch_usgs_earthquakes

# Core Runtime
from core.cluster_orchestrator import ClusterOrchestrator

# Research Engines
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI

# Unified Physics Kernel
from research.unified_physics_kernel import UnifiedPhysicsKernel


# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Research Simulation Dashboard")


# ----------------------------------------------------
# Engine Initialization
# ----------------------------------------------------

def init_engine(key, cls):
    if key not in st.session_state:
        st.session_state[key] = cls()
    return st.session_state[key]


cluster = init_engine("cluster", ClusterOrchestrator)

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

# Unified Physics Kernel
kernel = UnifiedPhysicsKernel(
    harmonic_engine,
    solver,
    tensor_engine
)


# ----------------------------------------------------
# Data Ingestion
# ----------------------------------------------------

st.header("🌎 Global Seismic Activity")

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
# Unified Physics Kernel Simulation
# ----------------------------------------------------

st.header("🧠 Unified Physics Simulation Kernel")

if df is not None and st.button("Run Unified Simulation"):

    result = kernel.run_simulation(df)

    st.metric(
        label="Unified Stability Index",
        value=f"{result['unified_stability_index']:.6f}"
    )

    st.json(result["components"])


# ----------------------------------------------------
# Discovery AI Panel
# ----------------------------------------------------

st.header("🤖 Autonomous Discovery AI")

if df is not None and st.button("Run Discovery Analysis"):

    discoveries = discovery_ai.analyze(df)

    st.json(discoveries)


# ----------------------------------------------------
# Cluster Execution Panel
# ----------------------------------------------------

st.header("📡 Research Cluster Runtime")

if st.button("Submit Research Task"):

    job_payload = {
        "task": "simulation_analysis",
        "dataset_rows": 0 if df is None else len(df)
    }

    job_id = cluster.submit_job(job_payload)

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
