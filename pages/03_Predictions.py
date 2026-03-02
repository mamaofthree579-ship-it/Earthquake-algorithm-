import streamlit as st
from ingest.usgs import fetch_usgs_week
from predictive.engine import score_from_mags

st.title("Predictions")

@st.cache_data(ttl=600)
def get_quakes():
    return fetch_usgs_week()

df = get_quakes()
if df is None or df.empty:
    st.error("Couldn’t fetch USGS data.")
    st.stop()

if "magnitude" not in df.columns:
    st.error("Feed missing magnitude column.")
    st.stop()

mags = df["magnitude"].tail(240).tolist()
prob = score_from_mags(mags)

st.metric("Elevated‑risk probability", f"{prob:.0%}")
st.caption(f"Using {len(mags)} recent quakes (max {max(mags):.1f})")
