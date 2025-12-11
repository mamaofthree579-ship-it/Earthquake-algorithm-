import streamlit as st
from predictive.engine import features_from_harmonics, load_model, predict
import pandas as pd
import numpy as np

st.title("Predictions — Risk Indices & Probability Cones")

st.write("This page demonstrates how a fitted model could be used to score harmonics features.")

st.info("This is a demo. Train a model using `predictive.train_demo_model` before running predictions.")

if st.button("Run demo scoring (synthetic)"):
    # create synthetic harmonics features
    n = 1024
    xf = np.linspace(0, 100, n//2)
    amp = np.random.rand(n//2) * 0.1
    amp[10] += 1.0  # inject a peak
    harmonics_df = pd.DataFrame({"freq": xf, "amp": amp})
    feats = features_from_harmonics(harmonics_df)
    st.write("Derived features:")
    st.json(feats.to_dict(orient="records"))
    model = load_model()
    if model is None:
        st.warning("No model artifact found. Use training routines to create a model first.")
    else:
        scores = predict(feats)
        st.success(f"Predicted risk score (0..1): {float(scores[0]):.3f}")
