import streamlit as st

from core.cluster_orchestrator import ClusterOrchestrator
from core.task_scheduler import TaskScheduler
from core.mesh_runtime import MeshRuntime
from governance.ethics_kernel import EthicsKernel
from research.artifact_ledger import ArtifactLedger


# ------------------------------------------------
# Page Configuration
# ------------------------------------------------

st.set_page_config(
    page_title="IHRAS Research Workstation",
    layout="wide"
)

st.title("🌍 IHRAS Institutional Research Dashboard")


# ------------------------------------------------
# System Initialization
# ------------------------------------------------

if "system" not in st.session_state:

    orchestrator = ClusterOrchestrator()
    scheduler = TaskScheduler(orchestrator)
    runtime = MeshRuntime(orchestrator)
    ethics = EthicsKernel()
    ledger = ArtifactLedger()

    st.session_state.system = {
        "orchestrator": orchestrator,
        "scheduler": scheduler,
        "runtime": runtime,
        "ethics": ethics,
        "ledger": ledger
    }

system = st.session_state.system


# ------------------------------------------------
# Sidebar Controls
# ------------------------------------------------

st.sidebar.header("Cluster Controls")

node_id = st.sidebar.text_input("Register Node ID")

if st.sidebar.button("Register Node"):
    if node_id:
        system["orchestrator"].register_node(node_id)
        st.sidebar.success(f"Node '{node_id}' registered")
    else:
        st.sidebar.warning("Enter a node ID")


st.sidebar.divider()

st.sidebar.subheader("Cluster Status")

nodes = system["orchestrator"].nodes

if nodes:
    for n in nodes:
        st.sidebar.write(f"🖥 {n}")
else:
    st.sidebar.info("No nodes registered")


# ------------------------------------------------
# Job Submission
# ------------------------------------------------

st.header("🔬 Submit Research Job")


def sample_compute():
    return {"value": 42}


if st.button("Run Sample Compute Job"):

    payload = {
        "compute": sample_compute
    }

    approved, message = system["ethics"].validate(payload)

    if not approved:
        st.error(message)

    else:

        job_id = system["orchestrator"].submit_job(payload)

        system["scheduler"].schedule()

        system["runtime"].execute(job_id)

        job = system["orchestrator"].jobs[job_id]

        # Record artifact
        artifact_hash = system["ledger"].record(job_id, job)

        job["artifact_hash"] = artifact_hash

        st.session_state["last_job"] = job


# ------------------------------------------------
# Job Output Section
# ------------------------------------------------

st.header("📊 Job Output")

if "last_job" in st.session_state:

    job = st.session_state["last_job"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Status", job.get("status", "N/A"))
    col2.metric("Node", job.get("node", "N/A"))
    col3.metric("Artifact Hash", job.get("artifact_hash", "Pending"))

    st.subheader("Job Result")

    st.json(job)

else:
    st.info("No job executed yet.")


# ------------------------------------------------
# Artifact Ledger Explorer
# ------------------------------------------------

st.header("📚 Artifact Ledger")

records = system["ledger"].load_all()

if records:

    st.write(f"Total Experiments Recorded: {len(records)}")

    for record in records:

        with st.expander(f"Experiment {record['job_id']}"):

            st.write("Timestamp:", record["timestamp"])
            st.write("Node:", record["node"])
            st.write("Status:", record["status"])
            st.write("Artifact Hash:", record["artifact_hash"])

            st.subheader("Result")

            st.json(record["result"])

else:

    st.info("No artifacts recorded yet.")


# ------------------------------------------------
# Footer
# ------------------------------------------------

st.divider()

st.caption("IHRAS • Integrated Harmonic Risk and Awareness System • Research Platform v1")
