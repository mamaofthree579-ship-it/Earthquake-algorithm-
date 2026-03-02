import streamlit as st
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import numpy as np

st.title("Predictions")

# load seed
historic = pd.read_csv(Path(__file__).parents[1] / "data" / "sample_quakes.csv")
live = st.session_state.get("quakes")
if live is not None:
    live = live.copy()
    live["solar_flare_window"] = 0
    df = pd.concat([historic, live], ignore_index=True)
else:
    df = historic

# numeric arrays only
mags = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0).values
flares = pd.to_numeric(df["solar_flare_window"], errors="coerce").fillna(0).values

# need enough rows
if len(mags) <= 120:
    st.warning("Not enough data yet.")
    st.stop()

X = np.array([np.append(mags[i-120:i], flares[i]) for i in range(120, len(mags))])
y = (mags[120:] > 5.5).astype(int)

if "model" not in st.session_state:
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(X, y)
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

latest = np.append(mags[-120:], flares[-1]).reshape(1, -1)
prob = clf.predict_proba(latest)[0, 1]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
