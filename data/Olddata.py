import streamlit as st, requests, pandas as pd
from datetime import datetime
from pathlib import Path
import pandas as pd

st.header("USGS pull")   # <-- this renders immediately

if st.button("Test call"):
    st.write("button pressed")   # if you see this, UI is working
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": "2024-01-01", "endtime": "2024-01-02"}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"})
    st.write("status", r.status_code)
    if r.status_code == 200:
        st.json(r.json())   # shows raw JSON – confirms we got data
raw = r.json() # r is the response from requests.get
rows = []
for f in raw["features"]:
    p = f["properties"]
    t = datetime.utcfromtimestamp(p["time"] / 1000.0)
    rows.append({
        "date": t.strftime("%Y-%m-%d"),
        "time": t.strftime("%H:%M:%S"),
        "place": p["place"], # e.g. "15 km S of Anza, CA"
        "magnitude": p["mag"] or 0,
        "solar_flare_window": 0
    })

df = pd.DataFrame(rows)
df.to_csv("data/sample_quakes.csv", index=False)
st.success(f"Converted {len(df)} records")
st.dataframe(df.head())
