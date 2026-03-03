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
    page_title="IHRAS Scientific Research Institute",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Scientific Theme Styling
# -----------------------------

st.markdown("""
<style>

body {
    background-color: #0E1117;
}

div.stButton > button {
    width: 100%;
}

.metric-card {
    padding: 15px;
    border-radius: 10px;
    background-color: #161B22;
    box-shadow: 0px 0px 8px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Control Panel
# -----------------------------

st.sidebar.title("🌍 IHRAS Research Control")

mode = st.sidebar.radio(
    "Dashboard Mode",
    [
        "Scientific Overview",
        "Simulation Kernel Monitor",
        "Federation Cluster Status",
        "Dataset Exploration"
    ]
)

st.sidebar.markdown("---")

# -----------------------------
# Load Streaming Research Data
# -----------------------------

df = fetch_usgs_stream()

# -----------------------------
# Scientific Overview Dashboard
# -----------------------------

if mode == "Scientific Overview":

    st.title("🌌 Open Science Research Platform")

    col1, col2 = st.columns(2)

    # Global Event Map
    with col1:

        st.subheader("🗺️ Global Research Event Distribution")

        if not df.empty:

            fig = render_global_map(
                df["longitude"].tolist(),
                df["latitude"].tolist(),
                df["magnitude"].tolist()
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Research stream unavailable")

    # Kernel Activity Metric
    with col2:

        st.subheader("🧠 Scientific Kernel Activity Index")

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
            title={"text": "Entropy Activity Index"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "#00FFAA"}
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Simulation Kernel Monitor
# -----------------------------

elif mode == "Simulation Kernel Monitor":

    st.title("🧪 Research Simulation Kernel")

    kernel = SolverKernel()

    if st.button("Run Scientific Kernel Step"):

        field = kernel.step()

        fig = go.Figure(
            go.Heatmap(
                z=field,
                colorscale="Viridis"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Federation Cluster Status
# -----------------------------

elif mode == "Federation Cluster Status":

    st.title("☁️ Scientific Cluster Federation")

    node_health = {
        "Compute Node A": np.random.rand(),
        "Compute Node B": np.random.rand(),
        "Compute Node C": np.random.rand(),
        "Compute Node D": np.random.rand()
    }

    fig = go.Figure(go.Bar(
        x=list(node_health.keys()),
        y=list(node_health.values())
    ))

    fig.update_layout(
        title="Research Cluster Health Index"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Dataset Explorer
# -----------------------------

elif mode == "Dataset Exploration":

    st.title("📊 Research Dataset Explorer")

    if df.empty:
        st.warning("No dataset stream available")

    else:
        st.dataframe(df)
