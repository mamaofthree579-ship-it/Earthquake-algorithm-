import streamlit as st
from predictive.engine import score_from_mags

st.title("Predictions")

# Pull the live DataFrame that the Map tab stored
df = st.session_state.get("quakes")
if df is None or df.empty:
    st.info("Open the Map tab first – it fetches the USGS feed.")
    st.stop()

mag_col = "magnitude" if "magnitude" in df.columns else None
if not mag_col:
    st.error("Magnitude column missing.")
    st.stop()

mags = df[mag_col].tail(240).tolist()
prob = score_from_mags(mags)

st.metric("Elevated‑risk probability", f"{prob:.0%}")
st.caption(f"Based on last {len(mags)} quakes; max {max(mags):.1f}")
