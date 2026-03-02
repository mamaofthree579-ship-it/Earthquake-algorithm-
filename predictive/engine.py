from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = Path(__file__).parent / "models" / "initial_rf.joblib"

def train_demo_model(X, y):
    """Fit a quick RandomForest and dump it to MODEL_PATH."""
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
