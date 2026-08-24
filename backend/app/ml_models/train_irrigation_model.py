import joblib

from pathlib import Path

from app.ml_models.irrigation_model import (
    train_irrigation_model
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "app"
    / "ml_models"
)

MODEL_FILE = (
    MODEL_DIR
    / "irrigation_model.pkl"
)

SCALER_FILE = (
    MODEL_DIR
    / "irrigation_scaler.pkl"
)


# =========================================================
# TRAIN AND SAVE
# =========================================================

def main():

    print(
        "Training irrigation model..."
    )

    # -----------------------------------------------------
    # TRAIN MODEL
    # -----------------------------------------------------

    model, scaler, accuracy = (
        train_irrigation_model()
    )

    # -----------------------------------------------------
    # CREATE DIRECTORY IF REQUIRED
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_FILE
    )

    # -----------------------------------------------------
    # SAVE SCALER
    # -----------------------------------------------------

    joblib.dump(
        scaler,
        SCALER_FILE
    )

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print()
    print(
        "Irrigation model trained successfully."
    )

    print(
        f"Model saved to: {MODEL_FILE}"
    )

    print(
        f"Scaler saved to: {SCALER_FILE}"
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print()
    print(
        "============================================================"
    )

    print(
        "IRRIGATION MODEL TRAINING COMPLETE"
    )

    print(
        "============================================================"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()