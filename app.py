import streamlit as st
import plotly.graph_objects as go
import numpy as np

from ingestion.usgs_stream import fetch_usgs_earthquakes

from core.cluster_orchestrator import ClusterOrchestrator

from research.autonomous_discovery import AutonomousDiscoveryEngine
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_engine import HarmonicTensorDiscoveryEngine
from research.autonomous_scientific_ai import AutonomousScientificDiscoveryAI
from research.self_referential_learning_loop import SelfReferentialDiscoveryLoop
from research.knowledge_singularity_stabilizer import KnowledgeCoherenceSingularityStabilizer


# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Integrated Harmonic Risk & Awareness System")


# ----------------------------------------------------
# Session State Initialization
# ----------------------------------------------------

if "cluster" not in st.session_state:
    st.session_state.cluster = ClusterOrchestrator()

if "discovery" not in st.session_state:
    st.session_state.discovery = AutonomousDiscoveryEngine()

if "harmonic_engine" not in st.session_state:
    st.session_state.harmonic_engine = PlanetaryHarmonicPredictionEngine()

if "solver" not in st.session_state:
    st.session_state.solver = SpacetimeCompressionSolver()

if "tensor_engine" not in st.session_state:
    st.session_state.tensor_engine = HarmonicTensorDiscoveryEngine()

if "ai_core" not in st.session_state:
    st.session_state.ai_core = AutonomousScientificDiscoveryAI()

if "learning_loop" not in st.session_state:
    st.session_state.learning_loop = SelfReferentialDiscoveryLoop()

if "stabilizer" not in st.session_state:
    st.session_state.stabilizer = KnowledgeCoherenceSingularityStabilizer()


cluster = st.session_state.cluster
discovery = st.session_state.discovery
harmonic_engine = st.session_state.harmonic_engine
solver = st.session_state.solver
tensor_engine = st.session_state.tensor_engine
ai_core = st.session_state.ai_core
learning_loop = st.session_state.learning_loop
stabilizer = st.session_state.stabilizer


# ----------------------------------------------------
# Seismic Visualization Layer
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
            geo=dict(projection_type="natural earth"),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Seismic feed unavailable.")

except Exception:
    st.warning("Ingestion subsystem offline.")


# ----------------------------------------------------
# Harmonic Forecast Simulation
# ----------------------------------------------------

st.header("🌌 Harmonic Hazard Forecast")

t = st.slider("Simulation Time Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):

    score = harmonic_engine.predict_risk(t)

    st.metric(
        label="Hazard Resonance Index",
        value=f"{score:.6f}"
    )


# ----------------------------------------------------
# Spacetime Compression Solver
# ----------------------------------------------------

st.header("🌀 Spacetime Compression Field Solver")

steps = st.slider("Solver Simulation Steps", 10, 100, 50)

if st.button("Run Compression Solver Simulation"):

    history = solver.simulate(steps)

    final_energy = float(np.mean(history[-1]))

    st.metric(
        label="Compression Field Energy",
        value=f"{final_energy:.6f}"
    )

    st.success("Solver simulation completed")


# ----------------------------------------------------
# Harmonic Tensor Discovery Scan
# ----------------------------------------------------

st.header("🧠 Harmonic Tensor Discovery Scan")

if st.button("Run Tensor Discovery Scan"):

    field = solver.field

    score = tensor_engine.discover(field)

    st.metric(
        label="Discovery Coherence Score",
        value=f"{score:.6f}"
    )


# ----------------------------------------------------
# Autonomous Scientific AI Cycle
# ----------------------------------------------------

st.header("🤖 Autonomous Scientific Discovery Cycle")

if st.button("Run Discovery Intelligence Cycle"):

    discovery_output = ai_core.discovery_cycle()

    learning_result = learning_loop.learning_cycle(discovery_output)

    st.metric(
        label="Self-Learning Stability Index",
        value=f"{learning_result['self_learning_score']:.6f}"
    )

    st.json(learning_result["metrics"])


# ----------------------------------------------------
# Singularity Stability Regulation
# ----------------------------------------------------

st.header("🧠 Knowledge Coherence Singularity Stabilizer")

if st.button("Run Stability Regulation Cycle"):

    signal = solver.field.flatten()

    result = stabilizer.stabilize(signal)

    st.metric(
        label="Singularity Stability Index",
        value=f"{result['stability_score']:.6f}"
    )

    st.json(result["metrics"])


# ----------------------------------------------------
# Cluster Experiment Console
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
        st.info("No artifact records found.")

except Exception:
    st.info("Ledger subsystem unavailable.")


# ----------------------------------------------------
# Platform Metrics Panel
# ----------------------------------------------------

st.header("📊 Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Dynamic")
col3.metric("Stored Artifacts", "Dynamic")


st.markdown("---")
st.caption("IHRAS Autonomous Scientific Research Platform")
