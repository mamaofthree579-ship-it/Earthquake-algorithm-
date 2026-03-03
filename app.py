import streamlit as st
import numpy as np

from ingestion.usgs_stream import fetch_stream
from core.solver_engine import ResearchSolverEngine
from visualization.geo_mapper import render_geo_map
from ensemble.monte_carlo_engine import monte_carlo_risk_simulation

st.set_page_config(layout="wide")

st.title("🌍 IHRAS Research Institute Platform")

# Load Data
df = fetch_stream()

# Solver Kernel
solver = ResearchSolverEngine()
field = solver.step()

# Visualization
fig = render_geo_map(df)
st.plotly_chart(fig, use_container_width=True)

# Risk Metric
risk_index = monte_carlo_risk_simulation(field)

st.metric(
    "Institute Risk Index (Research Proxy)",
    f"{risk_index:.5f}"
)
