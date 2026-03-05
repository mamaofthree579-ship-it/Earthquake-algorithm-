import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Ingestion Layer
from ingestion.usgs_stream import fetch_usgs_earthquakes

# Core Runtime
from core.cluster_orchestrator import ClusterOrchestrator

# Simulation Engines
from research.autonomous_discovery import AutonomousDiscoveryEngine
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_engine import HarmonicTensorDiscoveryEngine
from research.autonomous_scientific_ai import AutonomousScientificDiscoveryAI
from research.self_referential_learning_loop import SelfReferentialDiscoveryLoop
from research.knowledge_singularity_stabilizer import KnowledgeCoherenceSingularityStabilizer
from research.civilization_evolution_simulator import CivilizationKnowledgeEvolutionSimulator
from research.civilization_limit_theorem_engine import CivilizationLimitTheoremEngine
from research.civilization_singularity_field import CivilizationSingularityFieldCore
from research.omega_closure_field_engine import OmegaClosureFieldEngine
from research.universal_knowledge_mesh_core import UniversalKnowledgeMeshCore


# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Research Platform Prototype",
    layout="wide"
)

st.title("🌍 IHRAS Scientific Simulation Dashboard")


# ----------------------------------------------------
# Engine Initialization Helper
# ----------------------------------------------------

def init_engine(key, cls):
    if key not in st.session_state:
        st.session_state[key] = cls()
    return st.session_state[key]


# Initialize Systems
cluster = init_engine("cluster", ClusterOrchestrator)
harmonic_engine = init_engine("harmonic_engine", PlanetaryHarmonicPredictionEngine)
solver = init_engine("solver", SpacetimeCompressionSolver)
ai_core = init_engine("ai_core", AutonomousScientificDiscoveryAI)
learning_loop = init_engine("learning_loop", SelfReferentialDiscoveryLoop)
civilization_simulator = init_engine("civilization_simulator", CivilizationKnowledgeEvolutionSimulator)
singularity_core = init_engine("singularity_core", CivilizationSingularityFieldCore)
omega_engine = init_engine("omega_engine", OmegaClosureFieldEngine)
mesh_core = init_engine("mesh_core", UniversalKnowledgeMeshCore)


# ----------------------------------------------------
# Seismic Visualization
# ----------------------------------------------------

st.header("🌎 Global Seismic Activity")

try:
    df = fetch_usgs_earthquakes()

    if df is not None and not df.empty:

        df = df.dropna(subset=["longitude", "latitude", "magnitude"])

        df["magnitude"] = df["magnitude"].clip(lower=0.1)

        marker_size = (df["magnitude"] * 3).clip(lower=0.5)

        fig = go.Figure()

        fig.add_trace(
            go.Scattergeo(
                lon=df["longitude"],
                lat=df["latitude"],
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
# Harmonic Simulation Panel
# ----------------------------------------------------

st.header("🌌 Harmonic Simulation")

t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):
    score = harmonic_engine.predict_risk(t)

    st.metric(
        label="Hazard Resonance Index",
        value=f"{score:.6f}"
    )


# ----------------------------------------------------
# Compression Solver Simulation
# ----------------------------------------------------

st.header("🌀 Compression Solver")

steps = st.slider("Solver Steps", 10, 100, 50)

if st.button("Run Compression Simulation"):

    history = solver.simulate(steps)

    st.metric(
        label="Field Energy Estimate",
        value=f"{float(np.mean(history[-1])):.6f}"
    )


# ----------------------------------------------------
# Discovery Intelligence Cycle
# ----------------------------------------------------

st.header("🤖 Discovery Intelligence Cycle")

if st.button("Run Discovery Cycle"):

    discovery_output = ai_core.discovery_cycle()
    learning_result = learning_loop.learning_cycle(discovery_output)

    st.metric(
        label="Self-Learning Stability Index",
        value=f"{learning_result['self_learning_score']:.6f}"
    )

    st.json(learning_result["metrics"])


# ----------------------------------------------------
# Civilization Simulation
# ----------------------------------------------------

st.header("🌍 Civilization Knowledge Simulation")

steps = st.slider("Civilization Steps", 10, 100, 30)

if st.button("Run Civilization Simulation"):

    initial_state = np.random.randn(20)

    trajectory = civilization_simulator.simulate(
        initial_state,
        steps=steps
    )

    st.line_chart(np.array(trajectory))


# ----------------------------------------------------
# Singularity Field Analysis
# ----------------------------------------------------

st.header("🌌 Knowledge Singularity Field")

if st.button("Evaluate Singularity Field"):

    state_vector = np.random.randn(40)

    result = singularity_core.evaluate_field(state_vector)

    st.metric(
        label="Singularity Potential",
        value=f"{result['civilization_singularity_potential']:.6f}"
    )


# ----------------------------------------------------
# Omega Stability Engine
# ----------------------------------------------------

st.header("🌠 Omega Closure Stability")

if st.button("Run Omega Stability Evaluation"):

    state_vector = np.random.randn(50)

    result = omega_engine.evaluate(state_vector)

    st.metric(
        label="Omega Closure Index",
        value=f"{result['omega_closure_stability']:.6f}"
    )


# ----------------------------------------------------
# Knowledge Mesh Core
# ----------------------------------------------------

st.header("🌐 Universal Knowledge Mesh Core")

if st.button("Run Mesh Simulation"):

    field_state = np.random.randn(60)

    result = mesh_core.evaluate_mesh(field_state)

    st.metric(
        label="Mesh Coherence Index",
        value=f"{result['universal_mesh_coherence_score']:.6f}"
    )


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
# Platform Status
# ----------------------------------------------------

st.header("📊 Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Active")
col3.metric("Artifact Records", "Dynamic")


st.markdown("---")
st.caption("IHRAS Research Simulation Prototype")
