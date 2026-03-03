import streamlit as st
import numpy as np
import plotly.graph_objects as go

from ingestion.usgs_stream import fetch_usgs_stream
from core.solver_kernel import SolverKernel
from visualization.maps import render_global_map

# ------------------------------
# Page Configuration
# ------------------------------

st.set_page_config(
    page_title="IHRAS Next-Generation Research Lab",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Scientific Dark Theme Styling
# ------------------------------

st.markdown("""
<style>

body {
    background-color: #0B0F19;
}

.metric-box {
    padding: 20px;
    border-radius: 12px;
    background-color: #111827;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}

</style>
""", unsafe_allow_html=True)

# ------------------------------
# Sidebar Research Control Panel
# ------------------------------

st.sidebar.title("🌍 IHRAS Research Laboratory")

mode = st.sidebar.selectbox(
    "Scientific Workspace",
    [
        "Research Overview",
        "Simulation Engine",
        "Cluster Telemetry",
        "Dataset Laboratory"
    ]
)

st.sidebar.markdown("---")

# ------------------------------
# Streaming Research Data
# ------------------------------

df = fetch_usgs_stream()

# ------------------------------
# Research Overview Workspace
# ------------------------------

if mode == "Research Overview":

    st.title("🌌 Scientific Discovery Dashboard")

    col1, col2 = st.columns(2)

    # Global Event Map Panel
    with col1:

        st.subheader("🗺️ Global Research Activity Map")

        if not df.empty:

            fig = render_global_map(
                df["longitude"].tolist(),
                df["latitude"].tolist(),
                df["magnitude"].tolist()
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Research stream unavailable")

    # Scientific Kernel Activity Gauge
    with col2:

        st.subheader("🧠 Kernel Activity Telemetry")

        kernel = SolverKernel()
        field = kernel.step()

        entropy_proxy = float(
            np.mean(
                -field * np.log(np.abs(field) + 1e-8)
            )
        )

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=entropy_proxy,
            title={"text": "Scientific Activity Index"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "#00FFCC"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Simulation Engine Workspace
# ------------------------------

elif mode == "Simulation Engine":

    st.title("🧪 Research Simulation Laboratory")

    kernel = SolverKernel()

    if st.button("Run Simulation Step"):

        field = kernel.step()

        fig = go.Figure(
            go.Heatmap(
                z=field,
                colorscale="Viridis"
            )
        )

        fig.update_layout(
            title="Scientific Field Simulation Surface"
        )

        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Cluster Telemetry Workspace
# ------------------------------

elif mode == "Cluster Telemetry":

    st.title("☁️ Multi-Node Research Cluster Status")

    cluster_nodes = {
        "Compute Node Alpha": np.random.rand(),
        "Compute Node Beta": np.random.rand(),
        "Compute Node Gamma": np.random.rand(),
        "Compute Node Delta": np.random.rand()
    }

    fig = go.Figure(go.Bar(
        x=list(cluster_nodes.keys()),
        y=list(cluster_nodes.values())
    ))

    fig.update_layout(
        title="Federated Scientific Compute Health"
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# Dataset Laboratory Workspace
# ------------------------------

elif mode == "Dataset Laboratory":

    st.title("📊 Scientific Dataset Explorer")

    if df.empty:
        st.warning("No streaming research dataset available")

    else:
        st.dataframe(df)
