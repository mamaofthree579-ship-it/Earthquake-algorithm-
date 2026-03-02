import streamlit as st, requests, pandas as pd
from datetime import datetime
from pathlib import Path

st.header("USGS pull")   # <-- this renders immediately

if st.button("Test call"):
    st.write("button pressed")   # if you see this, UI is working
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": "2024-01-01", "endtime": "2024-01-02"}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"})
    st.write("status", r.status_code)
    if r.status_code == 200:
        st.json(r.json())   # shows raw JSON – confirms we got data
