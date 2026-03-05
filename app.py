import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from core.cluster_orchestrator import ClusterOrchestrator
from research.autonomous_discovery import AutonomousDiscoveryEngine
from research.harmonic_prediction_engine import PlanetaryHarmonicPredictionEngine
from ingestion.usgs_stream import fetch_usgs_earthquakes


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="IHRAS Scientific Hazard Research Platform",
    layout="wide"
)

st.title("🌍 IHRAS Integrated Harmonic Risk & Awareness System")


# --------------------------------------------------
# Initialize Core Engines
# --------------------------------------------------

if "cluster" not in st.session_state:
    st.session_state.cluster = ClusterOrchestrator()

if "discovery" not in st.session_state:
    st.session_state.discovery = AutonomousDiscoveryEngine()

if "harmonic_engine" not in st.session_state:
    st.session_state.harmonic_engine = PlanetaryHarmonicPredictionEngine()

cluster = st.session_state.cluster
discovery = st.session_state.discovery
harmonic_engine = st.session_state.harmonic_engine


# --------------------------------------------------
# Sidebar Controls
# --------------------------------------------------

st.sidebar.header("Research Controls")

if st.sidebar.button("Run Autonomous Discovery Cycle"):
    jobs = discovery.run_cycle(10)
    st.sidebar.success(f"Launched {len(jobs)} experiments")


# --------------------------------------------------
# Seismic Visualization Section
# --------------------------------------------------

st.header("🌎 Global Seismic Activity Map")

try:
    df = fetch_usgs_earthquakes()

    if df is not None and not df.empty:

        df = df.dropna(subset=["longitude", "latitude", "magnitude"])

        # Safety clamp magnitude values
        df["magnitude"] = df["magnitude"].apply(lambda x: max(float(x), 0.1))

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
        st.info("Seismic dataset currently unavailable.")

except Exception as e:
    st.warning("Seismic ingestion subsystem offline.")
    st.text(str(e))


# --------------------------------------------------
# Planetary Harmonic Forecast Engine
# --------------------------------------------------

st.header("🌌 Planetary Harmonic Risk Forecast")

t = st.slider("Simulation Time Index", 0, 365, 180)

if st.button("Run Harmonic Forecast Simulation"):

    risk_score = harmonic_engine.predict_risk(t)

    st.metric(
        label="Hazard Resonance Index",
        value=f"{risk_score:.5f}"
    )


# --------------------------------------------------
# Experiment Console
# --------------------------------------------------

st.header("🧪 Scientific Experiment Console")

param_x = st.number_input("Parameter X", value=1.0)
param_y = st.number_input("Parameter Y", value=2.0)

if st.button("Run Test Experiment"):

    def experiment(x, y):
        return {
            "experiment": "test_model",
            "parameters": {"x": x, "y": y},
            "result": float(x*x + y*y)
        }

    job_id = cluster.submit_job(
        experiment,
        param_x,
        param_y
    )

    st.success(f"Experiment job launched → {job_id}")


# --------------------------------------------------
# Artifact Ledger Viewer
# --------------------------------------------------

st.header("📚 Research Artifact Ledger")

try:
    artifacts = cluster.ledger.list_artifacts()

    if artifacts:
        for a in artifacts:
            st.code(a)
    else:
        st.info("No research artifacts stored.")

except Exception:
    st.info("Ledger subsystem unavailable.")


# --------------------------------------------------
# System Metrics Panel
# --------------------------------------------------

st.header("📊 Platform Status")

col1, col2, col3 = st.columns(3)

col1.metric("Cluster Nodes", "1")
col2.metric("Running Experiments", "Dynamic")
col3.metric("Artifact Records", "Dynamic")


st.markdown("---")
st.caption("IHRAS Autonomous Scientific Research Platform")
