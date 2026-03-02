import streamlit as st               # ← must be first
import pandas as pd
from predictive.engine import score_from_mags

st.title("Predictions")

# Grab the DataFrame — if it’s missing, explain and stop
df = st.session_state.get("quakes")
if df is None or df.empty:
    st.info("Open the Map tab first; it loads the live quake data.")
    st.stop()

# Defensive column pick
mag_col = "magnitude" if "magnitude" in df.columns else None
if mag_col is None:
    st.error("DataFrame has no magnitude column.")
    st.stop()

mags = df[mag_col].tail(240).tolist()
prob = score_from_mags(mags)

# Always show something
st.metric("Elevated‑risk probability", f"{prob:.0%}")
st.caption(f"Based on {len(mags)} recent quakes (max {max(mags):.1f})")
