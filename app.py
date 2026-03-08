import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ===============================
# Data Ingestion
# ===============================
from ingestion.usgs_stream import fetch_usgs_earthquakes

# ===============================
# Core Systems
# ===============================
from core.cluster_orchestrator import ClusterOrchestrator
from core.institutional_runtime_os import InstitutionalScientificRuntimeOS
from core.lineage_intelligence_core import LineageIntelligenceCore
from core.scientific_governance_layer import ScientificKnowledgeGovernanceLayer
from core.meta_os_kernel import MetaOSKernel
from core.scientific_memory_graph import ScientificMemoryGraph
from core.adaptive_experiment_intelligence import AdaptiveExperimentIntelligence

# ===============================
# Research Engines
# ===============================
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from research.spacetime_compression_solver import SpacetimeCompressionSolver
from research.harmonic_tensor_discovery import HarmonicTensorDiscovery
from research.discovery_fabric import AutonomousDiscoveryAI
from research.self_evolving_hypothesis import SelfEvolvingHypothesisEngine

# ===============================
# Streamlit Setup
# ===============================
st.set_page_config(
    page_title="IHRAS Autonomous Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Autonomous Research Platform")

# ===============================
# Engine Initialization Helper
# ===============================
def init_engine(key, factory):
    if key not in st.session_state:
        st.session_state[key] = factory()
    return st.session_state[key]

# ===============================
# Initialize Core & Research Engines
# ===============================
cluster = init_engine("cluster", ClusterOrchestrator)
runtime_os = init_engine("runtime_os", InstitutionalScientificRuntimeOS)
lineage_core = init_engine("lineage_core", LineageIntelligenceCore)
governance_layer = init_engine("governance_layer", ScientificKnowledgeGovernanceLayer)

harmonic_engine = init_engine("harmonic_engine", PlanetaryHarmonicPredictionEngine)
solver = init_engine("solver", SpacetimeCompressionSolver)
tensor_engine = init_engine("tensor_engine", HarmonicTensorDiscovery)
discovery_ai = init_engine("discovery_ai", AutonomousDiscoveryAI)

memory_graph = init_engine("memory_graph", ScientificMemoryGraph)
adaptive_ai = init_engine("adaptive_ai", lambda: AdaptiveExperimentIntelligence(memory_graph))

hypothesis_engine = init_engine(
    "hypothesis_engine",
    lambda: SelfEvolvingHypothesisEngine(memory_graph, None, adaptive_ai)
)

# ===============================
# Seismic Data Ingestion
# ===============================
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

# ===============================
# Map Visualization + Largest Magnitude
# ===============================
if df is not None and not df.empty:

    df = df.dropna(subset=["longitude", "latitude", "magnitude"])
    df["magnitude"] = df["magnitude"].abs().clip(lower=0.1)

    # ---- Global Map ----
    fig = go.Figure()
    fig.add_trace(
        go.Scattergeo(
            lon=df["longitude"],
            lat=df["latitude"],
            mode="markers",
            marker=dict(size=df["magnitude"] * 3, opacity=0.7)
        )
    )
    fig.update_layout(
        geo=dict(projection_type="natural earth"),
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- Largest Magnitude ----
    max_mag = df["magnitude"].max()
    max_row = df.loc[df["magnitude"] == max_mag].iloc[0]
    st.metric(
        label="Largest Earthquake Recorded",
        value=f"M {max_mag:.2f}",
        delta=max_row["place"] if "place" in df.columns else ""
    )

# =====================================================
# Temporal Seismic Evolution Tracker (Corrected)
# =====================================================

st.header("📈 Temporal Seismic Evolution Tracker")

# Always show slider
time_window = st.slider(
    "Select time window (days)",
    min_value=7,
    max_value=365,
    value=30,
    key="temporal_window_slider"
)

if df is not None and not df.empty:

    # Normalize time column if possible
    if "time" in df.columns:

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df_clean = df.dropna(subset=["time", "magnitude"])

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=time_window)

        df_window = df_clean[df_clean["time"] >= cutoff]

        if not df_window.empty:

            daily_max = df_window.groupby(
                df_window["time"].dt.date
            )["magnitude"].max()

            st.subheader("Seismic Energy Trend")

            st.line_chart(
                daily_max,
                height=400,
                use_container_width=True
            )

            st.caption(
                f"Showing maximum earthquake magnitude over the past {time_window} days."
            )

        else:
            st.info("No seismic events found in the selected time window.")

    else:
        st.warning("Dataset does not contain a usable time field.")

else:
    st.info("Seismic dataset currently unavailable.")

# ===============================
# Harmonic Prediction Panel
# ===============================
st.header("🌌 Harmonic Prediction Simulation")

t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):
    score = harmonic_engine.predict_risk(t)
    st.metric("Hazard Resonance Index", f"{score:.6f}")

# ===============================
# Self-Evolving Hypothesis Engine Panel
# ===============================
st.header("🧪 Self-Evolving Hypothesis Generation")

hypotheses_count = st.slider("Number of Hypotheses", 1, 10, 5)

if st.button("Run Hypothesis Discovery Cycle"):
    results = hypothesis_engine.discovery_cycle(n_candidates=int(hypotheses_count))
    st.success("Hypothesis Discovery Cycle Completed")
    st.json(results)

# ===============================
# Cluster Runtime Panel
# ===============================
st.header("📡 Research Cluster Runtime")

if st.button("Submit Cluster Task"):
    payload = {"task": "simulation_analysis", "dataset_rows": 0 if df is None else len(df)}
    job_id = cluster.submit_job(payload)
    st.success(f"Cluster job submitted: {job_id}")

# ===============================
# Footer Metrics
# ===============================
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Cluster Nodes", "1")
col2.metric("Research Cycles", "Active")
col3.metric("Artifacts", "Dynamic")
st.caption("IHRAS Autonomous Research Simulation Platform")
