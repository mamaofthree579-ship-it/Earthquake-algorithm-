import streamlit as st
import plotly.graph_objects as go

# -------------------------------
# Data Ingestion
# -------------------------------

from ingestion.usgs_stream import fetch_usgs_earthquakes

# -------------------------------
# Core Systems
# -------------------------------

from core.cluster_orchestrator import ClusterOrchestrator
from core.institutional_runtime_os import InstitutionalScientificRuntimeOS
from core.lineage_intelligence_core import LineageIntelligenceCore
from core.workflow_orchestrator import AutonomousWorkflowOrchestrator
from core.scientific_governance_layer import ScientificKnowledgeGovernanceLayer
from core.civilization_kernel import AutonomousScientificCivilizationKernel
from core.experiment_search_engine import AutomatedExperimentSearchEngine
from core.scientific_memory_graph import ScientificMemoryGraph
from core.adaptive_experiment_intelligence import AdaptiveExperimentIntelligence
from core.parallel_experiment_engine import ParallelExperimentEngine

# -------------------------------
# Research Engines
# -------------------------------

from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI

# -------------------------------
# Streamlit Setup
# -------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Scientific Simulation Dashboard")

# -------------------------------
# Session Initialization Helper
# -------------------------------

def init_engine(key, factory):

    if key not in st.session_state:
        st.session_state[key] = factory()

    return st.session_state[key]

# -------------------------------
# Initialize Core Systems
# -------------------------------

cluster = init_engine("cluster", ClusterOrchestrator)

runtime_os = init_engine(
    "runtime_os",
    InstitutionalScientificRuntimeOS
)

lineage_core = init_engine(
    "lineage_core",
    LineageIntelligenceCore
)

governance_layer = init_engine(
    "governance_layer",
    ScientificKnowledgeGovernanceLayer
)

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
    lambda: AutonomousWorkflowOrchestrator(
        cluster,
        lineage_core
    )
)

civilization_kernel = init_engine(
    "civilization_kernel",
    lambda: AutonomousScientificCivilizationKernel(
        workflow_orchestrator,
        governance_layer,
        lineage_core
    )
)

memory_graph = init_engine(
    "memory_graph",
    ScientificMemoryGraph
)

adaptive_ai = init_engine(
    "adaptive_ai",
    lambda: AdaptiveExperimentIntelligence(
        memory_graph
    )
)

experiment_search = init_engine(
    "experiment_search",
    lambda: AutomatedExperimentSearchEngine(
        civilization_kernel,
        adaptive_ai
    )
)

parallel_engine = init_engine(
    "parallel_engine",
    lambda: ParallelExperimentEngine(
        experiment_search,
        memory_graph
    )
)

# -------------------------------
# Data Ingestion
# -------------------------------

st.header("🌎 Global Seismic Activity")

df = None

try:
    df = fetch_usgs_earthquakes()

    if df is None or df.empty:
        st.warning("USGS data unavailable.")
        df = None

except Exception:
    st.warning("Data ingestion subsystem offline.")
    df = None

# -------------------------------
# Visualization Layer
# -------------------------------

if df is not None:

    df = df.dropna(subset=["longitude", "latitude", "magnitude"])
    df["magnitude"] = df["magnitude"].abs().clip(lower=0.1)

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            mode="markers",
            marker=dict(
                size=df["magnitude"] * 3,
                opacity=0.7
            )
        )
    )

    fig.update_layout(
        geo=dict(projection_type="natural earth"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Harmonic Simulation
# -------------------------------

st.header("🌌 Harmonic Prediction Simulation")

t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):

    score = harmonic_engine.predict_risk(t)

    st.metric(
        "Hazard Resonance Index",
        f"{score:.6f}"
    )

# -------------------------------
# Compression Solver
# -------------------------------

st.header("🌀 Compression Field Solver")

if df is not None and st.button("Run Compression Simulation"):

    result = solver.compute(df)

    st.json(result)

# -------------------------------
# Tensor Discovery
# -------------------------------

st.header("🔬 Harmonic Tensor Discovery")

if df is not None and st.button("Run Tensor Discovery"):

    result = tensor_engine.discover(df)

    st.json(result)

# -------------------------------
# Discovery AI
# -------------------------------

st.header("🤖 Autonomous Discovery AI")

if df is not None and st.button("Run Discovery Analysis"):

    result = discovery_ai.analyze(df)

    st.json(result)

# -------------------------------
# Workflow Kernel
# -------------------------------

st.header("⚙️ Autonomous Workflow Kernel")

if df is not None and st.button("Run Harmonic Workflow"):

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
        f"Workflow complete | Job {job_id} | Lineage {lineage_id}"
    )

    st.json(workflow_orchestrator.list_workflows())

# -------------------------------
# Civilization Kernel
# -------------------------------

st.header("🌌 Autonomous Civilization Kernel")

if df is not None and st.button("Run Research Cycle"):

    cycle = civilization_kernel.run_cycle(
        harmonic_engine,
        df
    )

    memory_graph.add_experiment(
        cycle["parameters"],
        cycle["result"],
        cycle["governance_index"]
    )

    st.json(cycle)

if st.button("Show Civilization Status"):

    status = civilization_kernel.civilization_status()

    st.metric("Total Research Cycles", status["total_cycles"])

    st.json(status["top_cycles"])

# -------------------------------
# Parallel Experiments
# -------------------------------

st.header("⚡ Parallel Experiment Engine")

parallel_runs = st.slider(
    "Parallel Experiments",
    1,
    20,
    5
)

if df is not None and st.button("Run Parallel Experiments"):

    results = parallel_engine.run_parallel_batch(
        harmonic_engine,
        df,
        parallel_runs
    )

    st.success(f"{len(results)} experiments completed")

    st.json(results)

# -------------------------------
# Memory Graph
# -------------------------------

st.header("🧠 Scientific Memory Graph")

if st.button("Memory Graph Summary"):

    summary = memory_graph.summary()

    st.metric(
        "Experiments Stored",
        summary["total_experiments"]
    )

    st.metric(
        "Connections",
        summary["connections"]
    )

# --------------------------------------------------
# Experimental Learning Parameter Predictor
# --------------------------------------------------

st.header("🧠 Experimental Learning Parameter Predictor")

if st.button("Generate Learning Parameter Prediction"):

    predicted_params = adaptive_ai.generate_parameters()

    st.success("Adaptive parameter prediction generated")

    st.json(predicted_params)

if st.button("View Memory-Guided Best Region Estimate"):

    experiments = memory_graph.nodes

    if len(experiments) == 0:
        st.info("No historical experiments available.")
    else:
        best_region = adaptive_ai.estimate_best_parameter()
        st.json(best_region)
        
# -------------------------------
# Cluster Runtime
# -------------------------------

st.header("📡 Cluster Runtime")

if st.button("Submit Cluster Task"):

    payload = {
        "task": "simulation_analysis",
        "dataset_rows": 0 if df is None else len(df)
    }

    job_id = cluster.submit_job(payload)

    st.success(f"Cluster job submitted: {job_id}")

# -------------------------------
# Platform Footer
# -------------------------------

st.markdown("---")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Active")
col3.metric("Artifacts", "Dynamic")

st.caption("IHRAS Research Simulation Prototype")
