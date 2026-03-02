import streamlit as st
import pandas as pd
import requests
from predictive.engine import score_from_mags

st.title("Predictions (real‑time)")

@st.cache_data(ttl=3600)
def load_usgs(days=7, min_mag=4.5):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": f"{pd.Timestamp.now() - pd.Timedelta(days=days):%Y-%m-%d}",
        "minmagnitude": min_mag,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    feats = r.json()["features"]
    rows = []
    for f in feats:
        p, g = f["properties"], f["geometry"]["coordinates"]
        rows.append({
            "time": pd.to_datetime(p["time"], unit="ms"),
            "magnitude": p["mag"],
            "lat": g[1],
            "lon": g[0],
        })
    return pd.DataFrame(rows)

try:
    df = load_usgs()
except Exception as e:
    st.error(f"Failed to fetch USGS data: {e}")
    st.stop()

if df.empty:
    st.warning("No quakes returned.")
    st.stop()

mags = df["magnitude"].tail(240).tolist()
prob = score_from_mags(mags)

st.metric("Elevated‑risk probability", f"{prob:.0%}")
st.caption(f"Based on {len(mags)} recent quakes (max {max(mags):.1f})")
