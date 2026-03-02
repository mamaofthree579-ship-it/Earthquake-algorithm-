import streamlit as st
import pandas as pd
from predictive.engine import score_from_mags

st.title("Predictions")

df: pd.DataFrame | None = st.session_state.get("quakes")
if df is None or df.empty:
    st.info("Open the Real‑time tab first and load data.")
    st.stop()

mag_col = "magnitude" if "magnitude" in df.columns else None
if mag_col is None:
    st.error("No magnitude column found.")
    st.stop()

mags = df[mag_col].tail(240).tolist()
prob = score_from_mags(mags)
st.metric("Elevated‑risk probability", f"{prob:.0%}")
