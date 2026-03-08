import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ===============================
# Data Ingestion & Persistence
# ===============================
from ingestion.usgs_stream import fetch_usgs_earthquakes
from core.artifact_ledger import ArtifactLedger

# ===============================
# Core Systems
# ===============================
from core.cluster_orchestrator import ClusterOrchestrator
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
# Streamlit Page Setup
# ===============================
st.set_page_config(page_title="IHRAS Research Platform", layout="wide")
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
ledger = init_engine("ledger", ArtifactLedger)

memory_graph = init_engine("memory_graph", ScientificMemoryGraph)
adaptive_ai = init_engine("adaptive_ai", lambda: AdaptiveExperimentIntelligence(memory_graph))

harmonic_engine = init_engine("harmonic_engine", PlanetaryHarmonicPredictionEngine)
solver = init_engine("solver", SpacetimeCompressionSolver)
tensor_engine = init_engine("tensor_engine", HarmonicTensorDiscovery)
discovery_ai = init_engine("discovery_ai", AutonomousDiscoveryAI)
hypothesis_engine = init_engine(
    "hypothesis_engine",
    lambda: SelfEvolvingHypothesisEngine(memory_graph, None, adaptive_ai)
)

# ===============================
# Seismic Data Ingestion
# ===============================
st.header("🌎 Global Seismic Activity")
df = None

# Attempt live ingestion
try:
    df_live = fetch_usgs_earthquakes()
    if df_live is not None and not df_live.empty:
        ledger.save_dataframe(df_live)  # Persist live observations
except Exception:
    st.warning("USGS ingestion subsystem offline.")

# Load historical data from ledger
df = ledger.load_dataframe()
if df is None or df.empty:
    st.warning("Seismic dataset unavailable.")

# ===============================
# Map + Largest Magnitude Display
# ===============================
if df is not None and not df.empty:
    df = df.dropna(subset=["longitude", "latitude", "magnitude"])
    df["magnitude"] = df["magnitude"].abs().clip(lower=0.1)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=df["longitude"],
        lat=df["latitude"],
        mode="markers",
        marker=dict(size=df["magnitude"] * 3, opacity=0.7)
    ))
    fig.update_layout(geo=dict(projection_type="natural earth"), height=600)
    st.plotly_chart(fig, use_container_width=True)

    max_mag = df["magnitude"].max()
    max_row = df.loc[df["magnitude"] == max_mag].iloc[0]
    st.metric(
        label="Largest Earthquake Recorded",
        value=f"M {max_mag:.2f}",
        delta=max_row["place"] if "place" in df.columns else ""
    )

# ===============================
# Temporal Seismic Evolution Tracker
# ===============================
st.header("📈 Temporal Seismic Evolution Tracker")
time_window = st.slider("Select historical observation window (days)", 7, 365, 30)

if df is not None and not df.empty:
    # Normalize timestamp
    if "time" in df.columns:
        df["event_time"] = pd.to_datetime(df["time"], errors="coerce")
    elif "datetime" in df.columns:
        df["event_time"] = pd.to_datetime(df["datetime"], errors="coerce")
    elif "date" in df.columns and "time" in df.columns:
        df["event_time"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str), errors="coerce")
    elif "date" in df.columns:
        df["event_time"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["event_time"] = None

    df_clean = df.dropna(subset=["event_time", "magnitude"])
    if not df_clean.empty:
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=time_window)
        df_window = df_clean[df_clean["event_time"] >= cutoff]

        if df_window.empty:
            st.info("No earthquake events recorded in this observation window.")
            st.caption(f"Dataset contains {len(df_clean)} total seismic events.")
        else:
            daily_max = df_window.groupby(df_window["event_time"].dt.date)["magnitude"].max()
            st.subheader("Seismic Energy Trend (Observed Data Only)")
            st.line_chart(daily_max, height=400, use_container_width=True)
    else:
        st.info("Dataset does not contain usable seismic records.")
else:
    st.info("Seismic ingestion feed currently unavailable.")

# ===============================
# Harmonic Prediction Simulation
# ===============================
st.header("🌌 Harmonic Prediction Simulation")
t = st.slider("Simulation Index", 0, 365, 180)

if st.button("Run Harmonic Simulation"):
    score = harmonic_engine.predict_risk(t)
    st.metric("Hazard Resonance Index", f"{score:.6f}")

# ===============================
# Self-Evolving Hypothesis Engine
# ===============================
st.header("🧪 Self-Evolving Hypothesis Generation")
hypotheses_count = st.slider("Number of Hypotheses", 1, 10, 5)

if st.button("Run Hypothesis Discovery Cycle"):
    results = hypothesis_engine.discovery_cycle(n_candidates=int(hypotheses_count))
    st.success("Hypothesis Discovery Cycle Completed")
    st.json(results)

# ===============================
# Compression Solver Simulation
# ===============================
st.header("🌀 Compression Solver")
steps = st.slider("Solver Steps", 10, 100, 50)

if st.button("Run Compression Simulation"):
    history = solver.simulate(steps)
    st.metric("Field Energy Estimate", f"{float(np.mean(history[-1])):.6f}")

# ===============================
# Tensor Discovery Engine Panel
# ===============================
st.header("🔬 Harmonic Tensor Discovery")

if st.button("Run Tensor Discovery"):
    tensor_result = tensor_engine.discover()
    st.json(tensor_result)

# ===============================
# Autonomous Discovery AI Panel
# ===============================
st.header("🤖 Autonomous Discovery AI")

if st.button("Run AI Discovery Cycle"):
    discovery_output = discovery_ai.run_cycle()
    st.metric("Autonomous Stability Index", f"{discovery_output['stability_score']:.6f}")
    st.json(discovery_output)

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
