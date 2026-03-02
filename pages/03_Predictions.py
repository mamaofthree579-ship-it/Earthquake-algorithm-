import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

st.title("Predictions")

# ---- load data ----
historic = pd.read_csv(Path(__file__).parents[1] / "data" / "sample_quakes.csv")
live = st.session_state.get("quakes")
df = pd.concat([historic, live], ignore_index=True) if live is not None else historic

mags = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0).values
flares = pd.to_numeric(df["solar_flare_window"], errors="coerce").fillna(0).values

if len(mags) <= 120:
    st.warning("Need >120 rows")
    st.stop()

# ---- fractal roughness helper ----
def hurst_exponent(series):
    n = len(series)
    if n < 3:
        return 0.0
    var1 = np.var(series[1:] - series[:-1])
    var2 = np.var(series[2:] - series[:-2])
    return 0.5 * np.log2(var2 / var1 + 1e-9)

# ---- build training matrix ----
X, y = [], []
for i in range(120, len(mags)):
    window = mags[i-120:i]
    h = hurst_exponent(window)
    X.append(np.append(np.append(window, flares[i]), h))
    y.append(1 if mags[i] > 5.5 else 0)

X = np.array(X)
y = np.array(y)

if len(np.unique(y)) < 2:
    st.warning("Add varied magnitudes")
    st.stop()

# ---- train / fetch model ----
if "model" not in st.session_state:
    clf = RandomForestClassifier(n_estimators=30, random_state=0)
    clf.fit(X, y)
    st.session_state["model"] = clf
else:
    clf = st.session_state["model"]

# ---- predict latest ----
latest_window = mags[-120:]
h_latest = hurst_exponent(latest_window)
latest = np.append(np.append(latest_window, flares[-1]), h_latest).reshape(1, -1)
prob = clf.predict_proba(latest)[0, 1]

st.metric("Elevated‑risk probability", f"{prob:.0%}")
# ---- where might it be? ----
# grab the last 120 rows' places
recent_places = df["place"].values[-120:]
# simple heuristic: if probability > 0.5, show the mode of recent places
if prob > 0.5:
    from collections import Counter
    top_place = Counter(recent_places).most_common(1)[0][0]
    st.write(f"Recent activity clusters near **{top_place}**")
else:
    st.write("No strong location signal")
