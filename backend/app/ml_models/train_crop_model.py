from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import train_test_split

from app.services.dataset_service import load_crop_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR /
    "app" /
    "ml_models" /
    "crop_model.pkl"
)


# =========================================================
# FEATURES
# =========================================================

FEATURE_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "temperature",
    "moisture",
    "rainfall"
]

TARGET_COLUMN = "crop"


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model():

    print("\n========================================")
    print("AI SMART AGRICULTURE")
    print("CROP MODEL TRAINING")
    print("========================================\n")

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    print("Loading crop dataset...")

    dataset = load_crop_data()

    print(
        f"Dataset rows: {len(dataset)}"
    )

    print(
        f"Crop classes: "
        f"{dataset[TARGET_COLUMN].nunique()}"
    )

    print("\nCrop distribution:")

    print(
        dataset[TARGET_COLUMN]
        .value_counts()
    )

    # -----------------------------------------------------
    # FEATURES / TARGET
    # -----------------------------------------------------

    X = dataset[
        FEATURE_COLUMNS
    ]

    y = dataset[
        TARGET_COLUMN
    ]

    # -----------------------------------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))

    # -----------------------------------------------------
    # RANDOM FOREST
    # -----------------------------------------------------

    print(
        "\nTraining Random Forest..."
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\n========================================")
    print("MODEL EVALUATION")
    print("========================================")

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print(
        "\nClassification Report:\n"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print(
        "\nConfusion Matrix:\n"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------

    print(
        "\nFeature Importance:\n"
    )

    importance = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "importance": model.feature_importances_
        }
    ).sort_values(
        "importance",
        ascending=False
    )

    print(
        importance.to_string(
            index=False
        )
    )

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"\nModel saved to:\n{MODEL_PATH}"
    )

    print(
        "\nCrop model training completed."
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    train_model()