import streamlit as st
import numpy as np
import plotly.graph_objects as go

from ingestion.usgs_stream import fetch_usgs_stream
from core.solver_kernel import SolverKernel
from visualization.maps import render_global_map

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="IHRAS Ultimate Research Workstation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Scientific Dark Workstation Theme
# -----------------------------

st.markdown("""
<style>

body {
    background-color: #050A14;
}

.metric-panel {
    padding: 18px;
    border-radius: 12px;
    background-color: #0F172A;
    box-shadow: 0px 0px 12px rgba(0,0,0,0.6);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Control Console
# -----------------------------

st.sidebar.title("🧠 IHRAS Control Console")

workspace = st.sidebar.radio(
    "Scientific Workspace",
    [
        "Telemetry Overview",
        "Simulation Field Monitor",
        "Cluster Federation Status",
        "Dataset Research Explorer"
    ]
)

st.sidebar.markdown("---")

# -----------------------------
# Streaming Research Dataset
# -----------------------------

df = fetch_usgs_stream()

# -----------------------------
# Workspace Routing
# -----------------------------

# =============================
# TELEMETRY OVERVIEW
# =============================

if workspace == "Telemetry Overview":

    st.title("🌌 Scientific Telemetry Dashboard")

    col1, col2 = st.columns(2)

    # Global Research Activity Map
    with col1:

        st.subheader("🗺️ Global Activity Surface")

        if not df.empty:

            fig = render_global_map(
                df["longitude"].tolist(),
                df["latitude"].tolist(),
                df["magnitude"].tolist()
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Research stream unavailable")

    # Kernel Activity Gauge Monitor
    with col2:

        st.subheader("🧠 Kernel Telemetry Index")

        kernel = SolverKernel()
        field = kernel.step()

        activity_index = float(
            np.mean(
                np.abs(field) *
                np.log(np.abs(field) + 1e-8)
            )
        )

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=activity_index,
            title={"text": "Scientific Activity Signal"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "#00FFD4"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

# =============================
# SIMULATION FIELD MONITOR
# =============================

elif workspace == "Simulation Field Monitor":

    st.title("🧪 Scientific Simulation Workspace")

    kernel = SolverKernel()

    if st.button("Execute Simulation Step"):

        field = kernel.step()

        fig = go.Figure(
            go.Heatmap(
                z=field,
                colorscale="Viridis"
            )
        )

        fig.update_layout(
            title="Research Simulation Field Surface"
        )

        st.plotly_chart(fig, use_container_width=True)

# =============================
# CLUSTER FEDERATION STATUS
# =============================

elif workspace == "Cluster Federation Status":

    st.title("☁️ Multi-Node Scientific Federation")

    cluster_nodes = {
        "Research Node Alpha": np.random.rand(),
        "Research Node Beta": np.random.rand(),
        "Research Node Gamma": np.random.rand(),
        "Research Node Delta": np.random.rand()
    }

    fig = go.Figure(go.Bar(
        x=list(cluster_nodes.keys()),
        y=list(cluster_nodes.values())
    ))

    fig.update_layout(
        title="Federated Compute Health Index"
    )

    st.plotly_chart(fig, use_container_width=True)

# =============================
# DATASET EXPLORER
# =============================

elif workspace == "Dataset Research Explorer":

    st.title("📊 Scientific Dataset Laboratory")

    if df.empty:
        st.warning("No research dataset stream available")

    else:
        st.dataframe(df)
