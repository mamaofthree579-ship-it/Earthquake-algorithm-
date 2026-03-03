import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.cluster_orchestrator import ClusterOrchestrator
from core.task_scheduler import TaskScheduler
from core.mesh_runtime import MeshRuntime
from governance.ethics_kernel import EthicsKernel

st.set_page_config(page_title="IHRAS Research Workstation", layout="wide")

st.title("🧬 IHRAS Institutional Research Dashboard")

# Initialize system once
if "system" not in st.session_state:
    orchestrator = ClusterOrchestrator()
    scheduler = TaskScheduler(orchestrator)
    runtime = MeshRuntime(orchestrator)
    ethics = EthicsKernel()

    st.session_state.system = {
        "orchestrator": orchestrator,
        "scheduler": scheduler,
        "runtime": runtime,
        "ethics": ethics
    }

system = st.session_state.system

# Register Node
st.sidebar.header("Cluster Controls")

node_id = st.sidebar.text_input("Register Node ID")

if st.sidebar.button("Register Node"):
    system["orchestrator"].register_node(node_id)
    st.sidebar.success("Node registered")

# Submit Job
st.header("🔬 Submit Research Job")

if st.button("Run Sample Compute Job"):

    def sample_compute():
        return {"value": 42}

    payload = {"compute": sample_compute}

    approved, message = system["ethics"].validate(payload)

    if not approved:
        st.error(message)
    else:
        job_id = system["orchestrator"].submit_job(payload)
        system["scheduler"].schedule()
        system["runtime"].execute(job_id)

        st.session_state["last_job"] = system["orchestrator"].jobs[job_id]

# Display Results
st.header("📊 Job Output")

if "last_job" in st.session_state:
    job = st.session_state["last_job"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Status", job.get("status", "N/A"))
    col2.metric("Node", job.get("node", "N/A"))
    col3.metric("Hash", job.get("hash", "Pending"))

    st.json(job)
else:
    st.info("No job submitted yet.")
