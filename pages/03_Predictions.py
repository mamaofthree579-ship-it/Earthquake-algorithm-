import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from ingest.usgs import fetch_usgs_week
from predictive.engine import features_from_harmonics, _mags_to_harmonics_df

st.title("Predictions")

@st.cache_data(ttl=600)
def get_quakes():
    return fetch_usgs_week()

df = get_quakes()
if df is None or df.empty or "magnitude" not in df.columns:
    st.error("No quake data.")
    st.stop()

# Train on‑the‑fly if model file missing
MODEL_PATH = Path(__file__).parents[1] / "predictive" / "models" / "initial_rf.joblib"
if not MODEL_PATH.exists():
    st.info("Training quick model…")
    X, y = [], []
    for i in range(120, len(df)):
        win = df["magnitude"].iloc[i-120:i].tolist()
        feats = features_from_harmonics(_mags_to_harmonics_df(win))
        X.append(feats.iloc[0])
        y.append(1 if df["magnitude"].iloc[i] > 5.5 else 0)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(pd.DataFrame(X), pd.Series(y))
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)

# Predict
model = joblib.load(MODEL_PATH)
mags = df["magnitude"].tail(240).tolist()
feats = features_from_harmonics(_mags_to_harmonics_df(mags))
prob = model.predict_proba(feats)[:, 1][0]
st.metric("Elevated‑risk probability", f"{prob:.0%}")
