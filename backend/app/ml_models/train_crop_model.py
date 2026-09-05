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

MODEL_DIR = (
    BASE_DIR /
    "app" /
    "ml_models" /
    "saved_models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR /
    "crop_random_forest.pkl"
)


# =========================================================
# FEATURES
# =========================================================

# IMPORTANT:
# These features MUST match:
#
# 1. crop_preprocessing.py
# 2. crop_model.py
# 3. crop dataset
#
# Crop model uses exactly 7 features.

FEATURE_COLUMNS = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "temperature",
    "humidity",
    "ph",
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
    # LOAD DATASET
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
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = (
        FEATURE_COLUMNS +
        [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:

        raise ValueError(
            "Crop dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # CONVERT NUMERICAL FEATURES
    # -----------------------------------------------------

    print("\nPreparing numerical features...")

    for column in FEATURE_COLUMNS:

        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # CLEAN TARGET
    # -----------------------------------------------------

    dataset[TARGET_COLUMN] = (
        dataset[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------------------------------
    # REMOVE INVALID ROWS
    # -----------------------------------------------------

    before_cleaning = len(dataset)

    dataset = dataset.dropna(
        subset=required_columns
    )

    dataset = dataset[
        dataset[TARGET_COLUMN].str.len() > 0
    ]

    dataset = dataset.reset_index(
        drop=True
    )

    removed_rows = (
        before_cleaning -
        len(dataset)
    )

    print(
        f"\nValid dataset rows: {len(dataset)}"
    )

    print(
        f"Invalid rows removed: {removed_rows}"
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

    print(
        "\nFeatures used by the model:"
    )

    for index, feature in enumerate(
        FEATURE_COLUMNS
    ):

        print(
            f"{index}: {feature}"
        )

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

    print(
        "\nTraining samples:",
        len(X_train)
    )

    print(
        "Testing samples:",
        len(X_test)
    )

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

    print(
        "\nGenerating predictions..."
    )

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
        f"Accuracy percentage: "
        f"{accuracy * 100:.2f}%"
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
    # MODEL INFORMATION
    # -----------------------------------------------------

    crop_classes = sorted(
        y.unique().tolist()
    )

    print(
        "\n========================================"
    )

    print(
        "MODEL INFORMATION"
    )

    print(
        "========================================"
    )

    print(
        f"Dataset records: {len(dataset)}"
    )

    print(
        f"Features: {len(FEATURE_COLUMNS)}"
    )

    print(
        f"Crop classes: {len(crop_classes)}"
    )

    print(
        f"Random Forest trees: "
        f"{model.n_estimators}"
    )

    print(
        f"Accuracy: "
        f"{accuracy * 100:.2f}%"
    )

    print(
        "\nCrop classes:"
    )

    for crop in crop_classes:

        print(
            f" - {crop}"
        )

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    print(
        "\nSaving model..."
    )

    model_package = {
        "model": model,
        "features": FEATURE_COLUMNS,
        "accuracy": float(accuracy),
        "dataset_records": int(len(dataset)),
        "crop_classes": crop_classes
    }

    joblib.dump(
        model_package,
        MODEL_PATH,
        compress=3
    )

    print(
        f"\nModel saved to:\n"
        f"{MODEL_PATH}"
    )

    print(
        "\n========================================"
    )

    print(
        "CROP MODEL TRAINING COMPLETED"
    )

    print(
        "========================================\n"
    )

    return model_package


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    train_model()