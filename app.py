import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("IHRAS Research Dashboard")

if st.button("Run Experiment"):

    r = requests.post(f"{API_URL}/submit_job")

    job_id = r.json()["job_id"]

    st.success(f"Job submitted: {job_id}")

job_id = st.text_input("Check Job Status")

if st.button("Check Status"):

    r = requests.get(f"{API_URL}/job_status/{job_id}")

    st.write(r.json())

if st.button("List Artifacts"):

    r = requests.get(f"{API_URL}/artifacts")

    st.write(r.json())

# ------------------------------------------------
# Footer
# ------------------------------------------------

st.divider()

st.caption("IHRAS • Integrated Harmonic Risk and Awareness System • Research Platform v1")
