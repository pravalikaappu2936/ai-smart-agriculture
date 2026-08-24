import joblib
from pathlib import Path

MODEL_DIR = Path("trained_models")
MODEL_DIR.mkdir(exist_ok=True)


def save_model(model, filename):
    joblib.dump(model, MODEL_DIR / filename)


def load_model(filename):
    return joblib.load(MODEL_DIR / filename)