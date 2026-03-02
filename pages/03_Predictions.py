import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

st.title("Predictions")

df = st.session_state.get("quakes")
if df is None or df.empty:
    st.info("Open Map first for data.")
    st.stop()

# use raw magnitudes as features: last 120 values
X, y = [], []
mags = df["magnitude"].tolist()
for i in range(120, len(mags)):
    X.append(mags[i-120:i]) # 120‑long window
    y.append(1 if mags[i] > 5.5 else 0)

if "model" not in st.session_state:
    st.info("Training tiny model…")
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(pd.DataFrame(X), pd.Series(y))
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

# predict from latest window
latest = mags[-120:]
prob = clf.predict_proba(pd.DataFrame([latest]))[0, 1]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
