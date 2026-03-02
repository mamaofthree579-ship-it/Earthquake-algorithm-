import streamlit as st
import pandas as pd
from predictive.engine import score_from_mags

st.title("Predictions")

df: pd.DataFrame | None = st.session_state.get("quakes")

if df is None or df.empty:
    st.warning("No quake data in session. Load some on the Ingestion tab first.")
else:
    mags = df["mag"].tail(240).tolist()
    try:
        prob = score_from_mags(mags)
        st.metric("Elevated-risk probability", f"{prob:.0%}")
    except Exception as exc:
        st.error("Prediction step failed.")
        st.code(f"{type(exc).__name__}: {exc}")
