import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="IHRAS Research Workstation",
    layout="wide"
)

st.title("🧬 IHRAS Institutional Research Dashboard")

# Sidebar
st.sidebar.header("Cluster Controls")

node_id = st.sidebar.text_input("Register Node ID")

if st.sidebar.button("Register Node"):
    r = requests.post(f"{API_URL}/register_node", params={"node_id": node_id})
    st.sidebar.success(r.json())

st.sidebar.divider()

# Submit Research Job
st.header("🔬 Submit Research Job")

if st.button("Run Sample Compute Job"):
    r = requests.post(f"{API_URL}/submit_job")
    st.session_state["last_job"] = r.json()

# Display Job Info
st.header("📊 Job Output")

if "last_job" in st.session_state:
    job = st.session_state["last_job"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Status", job.get("status", "N/A"))
    col2.metric("Node", job.get("node", "N/A"))
    col3.metric("Hash", job.get("hash", "Pending"))

    st.subheader("Full Job Record")
    st.json(job)

else:
    st.info("No job submitted yet.")

st.divider()

st.caption("IHRAS Scientific Compute Mesh • Stage 1 Hybrid Federation Ready")
