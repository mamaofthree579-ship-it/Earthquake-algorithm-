import streamlit as st
import pandas as pd
from predictive.engine import features_from_harmonics, _mags_to_harmonics_df, train_demo_model

df = st.session_state.get("quakes")
if df is None or df.empty:
    st.error("Load the Map tab first so we have data.")
    st.stop()

# Build a tiny supervised set: did a >5.5 quake follow the 120‑mag window?
X, y = [], []
for i in range(120, len(df)):
    window = df["magnitude"].iloc[i-120:i].tolist()
    feats = features_from_harmonics(_mags_to_harmonics_df(window))
    X.append(feats.iloc[0])
    y.append(1 if df["magnitude"].iloc[i] > 5.5 else 0)

train_demo_model(pd.DataFrame(X), pd.Series(y))
st.success("Model trained and saved as initial_rf.joblib")
