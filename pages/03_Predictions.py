import streamlit as st
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

st.title("Predictions")

historic = pd.read_csv(
    Path(__file__).parents[1] / "data" / "sample_quakes.csv"
)

live = st.session_state.get("quakes")
if live is not None:
    live = live.copy()
    live["solar_flare_window"] = 0
    df = pd.concat([historic, live], ignore_index=True)
else:
    df = historic

# force numeric only
mags = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0).tolist()
flares = pd.to_numeric(df["solar_flare_window"], errors="coerce").fillna(0).tolist()

X, y = [], []
for i in range(120, len(df)):
    X.append(mags[i-120:i] + [flares[i]])
    y.append(1 if mags[i] > 5.5 else 0)

if "model" not in st.session_state:
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(pd.DataFrame(X), pd.Series(y))
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

latest = mags[-120:] + [flares[-1]]
prob = clf.predict_proba(pd.DataFrame([latest]))[0, 1]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
