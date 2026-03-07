import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Ingestion
from ingestion.usgs_stream import fetch_usgs_earthquakes

# Core Runtime Layers
from core.cluster_orchestrator import ClusterOrchestrator
from core.institutional_runtime_os import InstitutionalScientificRuntimeOS
from core.lineage_intelligence_core import LineageIntelligenceCore
from core.workflow_orchestrator import AutonomousWorkflowOrchestrator
from core.scientific_governance_layer import ScientificKnowledgeGovernanceLayer

# Research Engines
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI


# ----------------------------------------------------
# Streamlit Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Scientific Simulation Dashboard")


# ----------------------------------------------------
# Engine Initialization Helper
# ----------------------------------------------------

def init_engine(key, factory):

    if key not in st.session_state:
        st.session_state[key] = factory()

    return st.session_state[key]


# ----------------------------------------------------
# Initialize Runtime Systems
# ----------------------------------------------------

cluster = init_engine("cluster", ClusterOrchestrator)
runtime_os = init_engine("runtime_os", InstitutionalScientificRuntimeOS)
lineage_core = init_engine("lineage_core", LineageIntelligenceCore)
governance_layer = init_engine("governance_layer", ScientificKnowledgeGovernanceLayer)

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

workflow_orchestrator = init_engine(
    "workflow_orchestrator",
    lambda: AutonomousWorkflowOrchestrator(cluster, lineage_core)
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
# Harmonic Prediction Simulation
# ----------------------------------------------------

st.header("🌌 Harmonic Prediction Simulation")

t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):

    score = harmonic_engine.predict_risk(t)

    st.metric(
        label="Hazard Resonance Index",
        value=f"{score:.6f}"
    )


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
# Discovery AI Engine
# ----------------------------------------------------

st.header("🤖 Autonomous Discovery AI")

if df is not None and st.button("Run Discovery Analysis"):

    result = discovery_ai.analyze(df)

    st.json(result)


# ----------------------------------------------------
# Workflow Orchestrator Kernel
# ----------------------------------------------------

st.header("⚙️ Autonomous Scientific Workflow Kernel")

if st.button("Run Full Harmonic Workflow"):

    task_id, job_id = workflow_orchestrator.schedule_task(
        "HarmonicPredictionEngine",
        harmonic_engine.predict_risk,
        df=df,
        parameters={"t": 180}
    )

    result = {
        "hazard_index": harmonic_engine.predict_risk(180)
    }

    lineage_id = workflow_orchestrator.complete_task(
        task_id,
        df=df,
        parameters={"t": 180},
        result=result
    )

    st.success(
        f"Workflow Completed | Job {job_id} | Lineage {lineage_id}"
    )

    st.json(workflow_orchestrator.list_workflows())


# ----------------------------------------------------
# Governance Monitoring Panel
# ----------------------------------------------------

st.header("🧠 Scientific Knowledge Governance Monitor")

if df is not None and st.button("Evaluate Governance Integrity"):

    governance_result = governance_layer.evaluate_governance(
        df,
        {"simulation": "dashboard_run"}
    )

    st.metric(
        label="Governance Integrity Index",
        value=f"{governance_result['governance_index']:.6f}"
    )

    st.json(governance_result)


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
# Artifact Ledger Viewer
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

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Active")
col3.metric("Artifact Records", "Dynamic")

st.caption("IHRAS Research Simulation Prototype")
