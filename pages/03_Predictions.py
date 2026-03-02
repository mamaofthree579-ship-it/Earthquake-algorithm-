import streamlit as st, pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

st.title("Predictions")

historic = pd.read_csv(Path(__file__).parents[1] / "data" / "sample_quakes.csv")
live = st.session_state.get("quakes")
df = pd.concat([historic, live], ignore_index=True) if live is not None else historic

mags = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0).values
flares = pd.to_numeric(df["solar_flare_window"], errors="coerce").fillna(0).values

if len(mags) <= 120:
    st.warning("Need >120 rows")
    st.stop()

X = np.array([np.append(mags[i-120:i], flares[i]) for i in range(120, len(mags))])
# use median as dynamic threshold → guarantees both classes if data varies
threshold = np.median(mags[120:])
y = (mags[120:] > threshold).astype(int)

if len(np.unique(y)) < 2:
    st.warning("All mags identical; add varied data")
    st.stop()

if "model" not in st.session_state:
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(X, y)
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

latest = np.append(mags[-120:], flares[-1]).reshape(1, -1)
prob = clf.predict_proba(latest)[0, 1]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
