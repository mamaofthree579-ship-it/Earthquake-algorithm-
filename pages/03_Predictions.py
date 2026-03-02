# predictive/engine.py
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).parent / "models" / "initial_rf.joblib"

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None

def predict(feat_df):
    model = load_model()
    if model is None:
        return np.zeros(len(feat_df))
    return model.predict_proba(feat_df)[:, 1]

def score_from_mags(mags):
    # placeholder feature build — replace with your real logic
    f = pd.DataFrame([mags])
    return float(predict(f)[0])

def train_demo_model(X, y):
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
