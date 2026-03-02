import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from sklearn.linear_model import LogisticRegression

st.header("Predictions")

csv_path = Path(__file__).parents[1] / "data" / "sample_quakes.csv"

# ---- optional fetch ----
if st.button("Load 2023 USGS data"):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        "format=geojson&starttime=2023-01-01&endtime=2023-12-31"
    )
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "eq-demo"})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        st.error(f"USGS fetch failed: {e}")
    else:
        rows = []
        for f in data["features"]:
            p = f["properties"]
            t = datetime.utcfromtimestamp(p["time"] / 1000.0)
            rows.append({
                "date": t.strftime("%Y-%m-%d"),
                "time": t.strftime("%H:%M:%S"),
                "place": p["place"],
                "magnitude": p["mag"] if p["mag"] is not None else 0,
                "solar_flare_window": 0
            })
        pd.DataFrame(rows).to_csv(csv_path, index=False)
        st.success("Historical data written")

# ---- model ----
df = pd.read_stem(csv_path)
if len(df) < 130:
    st.warning("Need ~130 rows for stable training")
    st.stop()

mags = df["magnitude"].values.astype(float)
F = df["solar_flare_window"].values.astype(int)
X, y = [], []
for i in range(120, len(mags)):
    X.append([np.mean(mags[i-120:i]), np.std(mags[i-120:i]), F[i]])
    y.append(int(mags[i] > 5.5))
X = np.array(X)
y = np.array(y)
if len(set(y)) < 2:
    st.error("No class variety – check magnitudes")
    st.stop()

clf = LogisticRegression(solver="lbfgs").fit(X, y)
prob = clf.predict_proba([[mags[-120:].mean(), mags[-120:].std(), F[-1]]])[0][1]

st.metric("Elevated‑risk probability", f"{prob:.0%}")

# ---- top places ----
probs = clf.predict_proba(X)[:, 1]
high_idx = np.where(probs > 0.5)[0]
if high_idx.size:
    top = df.iloc[high_idx + 120]["place"].value_counts().head(5)
    st.subheader("Top places in recent risky windows")
    for place, cnt in top.items():
        st.write(f"{place} – {cnt} recent windows")
else:
    st.write("No high‑risk windows found")
