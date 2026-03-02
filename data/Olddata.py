import streamlit as st
import requests, pandas as pd
from datetime import datetime
from pathlib import Path

st.header("Load historical USGS data")

if st.button("Fetch 2023 quakes"):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        "format=geojson&starttime=2023-01-01&endtime=2023-12-31"
    )
    r = requests.get(url)
    data = r.json()

    rows = []
    for f in data["features"]:
        p = f["properties"]
        t = datetime.utcfromtimestamp(p["time"] / 1000.0)
        rows.append({
            "date": t.strftime("%Y-%m-%d"),
            "time": t.strftime("%H:%M:%S"),
            "place": p["place"],
            "magnitude": p["mag"] if p["mag"] is not None else 0,
            "solar_flare_window": 0
        })
    old_df = pd.DataFrame(rows)
    csv_path = Path(__file__).parents[1] / "data" / "sample_quakes.csv"
    old_df.to_csv(csv_path, index=False)
    st.success(f"Saved {len(old_df)} rows")
