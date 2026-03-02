# pages/02_Load_Data.py
import streamlit as st
import requests, pandas as pd
from datetime import datetime
from pathlib import Path

st.title("Fetch USGS data → CSV")

# input dates
start = st.text_input("Start (YYYY‑MM‑DD)", "2024‑01‑01")
end   = st.text_input("End (YYYY‑MM‑DD)",   "2024‑01‑07")

if st.button("Run"):
    # --- same request that worked in test pool ---
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": start, "endtime": end}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"}, timeout=15)
    st.write("HTTP status:", r.status_code)

    if r.status_code != 200:
        st.error("Request failed")
        st.write(r.text[:200])
        st.stop()

    raw = r.json()
    rows = []
    for f in raw["features"]:
        p = f["properties"]
        t = datetime.utcfromtimestamp(p["time"] / 1000.0)
        rows.append({
            "date": t.strftime("%Y-%m-%d"),
            "time": t.strftime("%H:%M:%S"),
            "place": p["place"],
            "magnitude": p["mag"] or 0,
            "solar_flare_window": 0
        })

    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No data returned")
    else:
        out = Path("data/sample_quakes.csv")
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        st.success(f"Saved {len(df)} rows")
        st.dataframe(df.head())
