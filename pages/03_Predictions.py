import streamlit as st
import pandas as pd
from predictive.engine import score_from_mags

st.title("Predictions")

df: pd.DataFrame | None = st.session_state.get("quakes")

if df is None or df.empty:
    st.info("Open the Real‑time tab first and load data.")
    st.stop()

# Show exactly what we received
st.write("DataFrame shape:", df.shape)
st.write("Column list:", list(df.columns))
st.dataframe(df.head(3))

# Choose magnitude column
mag_col = None
for c in ["mag", "magnitude", "mag_value"]:
    if c in df.columns:
        mag_col = c
        break
if mag_col is None:
    nums = df.select_dtypes(include="number").columns.tolist()
    mag_col = nums[0] if nums else None

if not mag_col:
    st.error("No numeric column found. Check the Real‑time tab.")
    st.stop()

mags = df[mag_col].tail(240).tolist()
prob = score_from_mags(mags)
st.metric("Elevated‑risk probability", f"{prob:.0%}")
