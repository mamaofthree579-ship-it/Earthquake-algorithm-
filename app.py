import streamlit as st
from core.cluster_orchestrator import ClusterOrchestrator
from experiments.example_experiment import run_experiment

st.title("IHRAS Research Dashboard")

cluster = ClusterOrchestrator()

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if st.button("Run Experiment"):

    params = {"x": 5, "y": 10}

    job_id = cluster.submit_job(run_experiment, params)

    st.session_state.jobs.append(job_id)

    st.success(f"Job submitted: {job_id}")

st.header("Job Status")

for job_id in st.session_state.jobs:

    status = cluster.job_status(job_id)

    st.write(job_id, status)

st.header("Artifacts")

if st.button("List Artifacts"):

    artifacts = cluster.ledger.list_artifacts()

    st.write(artifacts)
