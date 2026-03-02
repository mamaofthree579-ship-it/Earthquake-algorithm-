import joblib
from pathlib import Path
import numpy as np

MODEL_PATH = Path(__file__).parent / "models" / "initial_rf.joblib"

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except Exception: # catches ModuleNotFoundError, EOFError, etc.
        return None # signal “no model”

def predict(feat_df):
    model = load_model()
    if model is None:
        # fallback: zero probability for every row
        return np.zeros(len(feat_df))
    return model.predict_proba(feat_df)[:, 1]

def score_from_mags(mags):
    # …build features df called `f`…
    return float(predict(f)[0])
