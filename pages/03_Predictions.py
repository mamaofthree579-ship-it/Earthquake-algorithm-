import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

st.title("Predictions")

# grab live data if Map ran
live = st.session_state.get("quakes")

# load historic sample
historic = pd.read_csv(Path(__file__).parents[1] / "data" / "sample_quakes.csv")

df = pd.concat([historic, live], ignore_index=True) if live is not None else historic

mags = df["magnitude"].tolist()
X, y = [], []
for i in range(120, len(mags)):
    X.append(mags[i-120:i])
    y.append(1 if mags[i] > 5.5 else 0)

if "model" not in st.session_state:
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(pd.DataFrame(X), pd.Series(y))
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

prob = clf.predict_proba(pd.DataFrame([mags[-120:]]))[0, 1]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
