import joblib
from pathlib import Path
import numpy as np

MODEL_PATH = Path(__file__).parent / "models" / "initial_rf.joblib"

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        # Model missing or unpickling failed – return None
        return None

def predict(feat_df):
    model = load_model()
    if model is None:
        # Neutral fallback: always predicts 0 (no elevated risk)
        return np.array([0.0])
    return model.predict_proba(feat_df)[:, 1]

def score_from_mags(mags):
    # …build features df `f`…
    return float(predict(f)[0])
