import streamlit as st
import plotly.graph_objects as go
import numpy as np

from ingestion.usgs_stream import fetch_usgs_earthquakes
from core.cluster_orchestrator import ClusterOrchestrator
from research.autonomous_discovery import AutonomousDiscoveryEngine
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver


# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Integrated Harmonic Risk & Awareness System")


# ----------------------------------------------------
# Initialize Systems (Session Safe)
# ----------------------------------------------------

if "cluster" not in st.session_state:
    st.session_state.cluster = ClusterOrchestrator()

if "discovery" not in st.session_state:
    st.session_state.discovery = AutonomousDiscoveryEngine()

if "harmonic_engine" not in st.session_state:
    st.session_state.harmonic_engine = PlanetaryHarmonicPredictionEngine()

if "solver" not in st.session_state:
    st.session_state.solver = SpacetimeCompressionSolver()

cluster = st.session_state.cluster
discovery = st.session_state.discovery
harmonic_engine = st.session_state.harmonic_engine
solver = st.session_state.solver


# ----------------------------------------------------
# Sidebar Research Controls
# ----------------------------------------------------

st.sidebar.header("Autonomous Research Controls")

if st.sidebar.button("Run Discovery Cycle"):
    jobs = discovery.run_cycle(10)
    st.sidebar.success(f"Autonomous experiments launched: {len(jobs)}")


# ----------------------------------------------------
# Seismic Visualization
# ----------------------------------------------------

st.header("🌎 Global Seismic Activity")

try:
    df = fetch_usgs_earthquakes()

    if df is not None and not df.empty:

        df = df.dropna(subset=["longitude", "latitude", "magnitude"])

        df["magnitude"] = df["magnitude"].apply(
            lambda x: max(float(x), 0.1)
        )

        marker_size = (df["magnitude"] * 3).clip(lower=0.5)

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
        st.info("Seismic feed unavailable.")

except Exception:
    st.warning("Hazard ingestion subsystem offline.")


# ----------------------------------------------------
# Planetary Harmonic Forecast Engine
# ----------------------------------------------------

st.header("🌌 Harmonic Hazard Forecast Simulator")

t = st.slider("Simulation Time Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):

    score = harmonic_engine.predict_risk(t)

    st.metric(
        label="Hazard Resonance Index",
        value=f"{score:.6f}"
    )


# ----------------------------------------------------
# Spacetime Compression Solver Simulation
# ----------------------------------------------------

st.header("🌀 Spacetime Compression Field Solver")

steps = st.slider("Solver Simulation Steps", 10, 100, 50)

if st.button("Run Compression Simulation"):

    history = solver.simulate(steps)

    final_state = np.mean(history[-1])

    st.metric(
        label="Compression Field Mean Energy",
        value=f"{final_state:.6f}"
    )

    st.success("Simulation completed")


# ----------------------------------------------------
# Experiment Console
# ----------------------------------------------------

st.header("🧪 Scientific Experiment Console")

x = st.number_input("Parameter X", value=1.0)
y = st.number_input("Parameter Y", value=2.0)

if st.button("Run Test Experiment"):

    def experiment(x, y):
        return {
            "experiment": "test_model",
            "parameters": {"x": x, "y": y},
            "result": float(x*x + y*y)
        }

    job_id = cluster.submit_job(
        experiment,
        x,
        y
    )

    st.success(f"Experiment job launched → {job_id}")


# ----------------------------------------------------
# Artifact Ledger Viewer
# ----------------------------------------------------

st.header("📚 Research Artifact Ledger")

try:
    artifacts = cluster.ledger.list_artifacts()

    if artifacts:
        for a in artifacts:
            st.code(a)
    else:
        st.info("No artifact records.")

except Exception:
    st.info("Ledger subsystem unavailable.")


# ----------------------------------------------------
# Platform Metrics Panel
# ----------------------------------------------------

st.header("📊 Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Active Research Cycles", "Dynamic")
col3.metric("Stored Artifacts", "Dynamic")


st.markdown("---")
st.caption("IHRAS Autonomous Scientific Research Platform")
