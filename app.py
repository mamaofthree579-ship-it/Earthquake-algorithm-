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
from research.civilization_evolution_simulator import CivilizationKnowledgeEvolutionSimulator
from research.civilization_limit_theorem_engine import CivilizationLimitTheoremEngine


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

def init_engine(key, cls):
    if key not in st.session_state:
        st.session_state[key] = cls()
    return st.session_state[key]


cluster = init_engine("cluster", ClusterOrchestrator)
discovery = init_engine("discovery", AutonomousDiscoveryEngine)
harmonic_engine = init_engine("harmonic_engine", PlanetaryHarmonicPredictionEngine)
solver = init_engine("solver", SpacetimeCompressionSolver)
tensor_engine = init_engine("tensor_engine", HarmonicTensorDiscoveryEngine)
ai_core = init_engine("ai_core", AutonomousScientificDiscoveryAI)
learning_loop = init_engine("learning_loop", SelfReferentialDiscoveryLoop)
stabilizer = init_engine("stabilizer", KnowledgeCoherenceSingularityStabilizer)
civilization_simulator = init_engine("civilization_simulator", CivilizationKnowledgeEvolutionSimulator)
civilization_limit_engine = init_engine("civilization_limit_engine", CivilizationLimitTheoremEngine)


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

if st.button("Run Compression Simulation"):

    history = solver.simulate(steps)

    final_energy = float(np.mean(history[-1]))

    st.metric(
        label="Compression Field Energy",
        value=f"{final_energy:.6f}"
    )


# ----------------------------------------------------
# Discovery Intelligence Cycle
# ----------------------------------------------------

st.header("🤖 Autonomous Discovery Intelligence Cycle")

if st.button("Run Discovery Cycle"):

    discovery_output = ai_core.discovery_cycle()

    learning_result = learning_loop.learning_cycle(discovery_output)

    st.metric(
        label="Self-Learning Stability Index",
        value=f"{learning_result['self_learning_score']:.6f}"
    )

    st.json(learning_result["metrics"])


# ----------------------------------------------------
# Civilization Knowledge Evolution Simulation
# ----------------------------------------------------

st.header("🌍 Civilization Knowledge Evolution Simulator")

steps = st.slider("Civilization Evolution Steps", 10, 100, 30)

if st.button("Run Civilization Simulation"):

    initial_state = np.random.randn(20)

    trajectory = civilization_simulator.simulate(
        initial_state,
        steps=steps
    )

    st.line_chart(np.array(trajectory))


# ----------------------------------------------------
# Civilization Knowledge Limit Analysis
# ----------------------------------------------------

st.header("🌌 Civilization Knowledge Limit Stability Analysis")

if st.button("Run Civilization Limit Evaluation"):

    state_vector = np.random.randn(30)

    result = civilization_limit_engine.evaluate(state_vector)

    st.metric(
        label="Civilization Limit Stability Score",
        value=f"{result['civilization_limit_score']:.6f}"
    )

    st.json(result["metrics"])


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
col2.metric("Research Cycles", "Active")
col3.metric("Artifact Records", "Dynamic")


st.markdown("---")
st.caption("IHRAS Autonomous Scientific Research Platform")
