import streamlit as st
from predictive.engine import score_from_mags

df = st.session_state.get("quakes")
if df is None or df.empty:
    st.info("Open the Map tab first to load real‑time data.")
    st.stop()

mags = df["magnitude"].tail(240).tolist()
prob = score_from_mags(mags)
st.metric("Elevated‑risk probability", f"{prob:.0%}")
