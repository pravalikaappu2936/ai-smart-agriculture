from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_crop_data


# =========================================================
# MODEL CONFIGURATION
# =========================================================

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
# MODEL FILE
# =========================================================

MODEL_DIR = (
    Path(__file__).resolve().parent
    / "saved_models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR
    / "crop_random_forest.pkl"
)


# =========================================================
# TRAIN MODEL
# =========================================================

def train_crop_model():
    """
    Train the Random Forest crop recommendation model
    using the complete crop dataset.
    """

    dataset = load_crop_data()

    if dataset is None or dataset.empty:
        raise ValueError(
            "Crop dataset is empty."
        )

    # -----------------------------------------------------
    # Check columns
    # -----------------------------------------------------

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in dataset.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in crop dataset: "
            + ", ".join(missing_columns)
        )

    dataset = dataset.copy()

    # -----------------------------------------------------
    # Convert numerical columns
    # -----------------------------------------------------

    for column in FEATURE_COLUMNS:

        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean crop labels
    # -----------------------------------------------------

    dataset[TARGET_COLUMN] = (
        dataset[TARGET_COLUMN]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    dataset = dataset.dropna(
        subset=FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    dataset = dataset[
        dataset[TARGET_COLUMN] != ""
    ]

    if dataset.empty:
        raise ValueError(
            "No valid crop records available."
        )

    # -----------------------------------------------------
    # Prepare X and y
    # -----------------------------------------------------

    X = dataset[
        FEATURE_COLUMNS
    ]

    y = dataset[
        TARGET_COLUMN
    ]

    # -----------------------------------------------------
    # Train/test split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # -----------------------------------------------------
    # Random Forest
    # -----------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    model_data = {
        "model": model,
        "features": FEATURE_COLUMNS,
        "accuracy": float(accuracy),
        "dataset_records": int(len(dataset)),
        "crop_classes": sorted(
            y.unique().tolist()
        )
    }

    joblib.dump(
        model_data,
        MODEL_PATH
    )

    print(
        "=========================================="
    )

    print(
        "CROP MODEL TRAINED"
    )

    print(
        "=========================================="
    )

    print(
        f"Dataset records : {len(dataset)}"
    )

    print(
        f"Crop classes    : {len(y.unique())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print(
        "=========================================="
    )

    return model_data


# =========================================================
# LOAD MODEL
# =========================================================

def load_crop_model():
    """
    Load the trained crop model.

    If the model does not exist, automatically train it.
    """

    if not MODEL_PATH.exists():

        print(
            "Crop model not found."
        )

        print(
            "Training new Random Forest model..."
        )

        return train_crop_model()

    try:

        model_data = joblib.load(
            MODEL_PATH
        )

        return model_data

    except Exception as error:

        print(
            "Unable to load crop model."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Retraining crop model..."
        )

        return train_crop_model()


# =========================================================
# PREDICT CROP
# =========================================================

def predict_crop(features):
    """
    Predict the most suitable crop.

    Returns:

        recommended crop
    """

    # -----------------------------------------------------
    # Convert input
    # -----------------------------------------------------

    features = np.asarray(
        features,
        dtype=float
    )

    # -----------------------------------------------------
    # Handle (1, 7)
    # -----------------------------------------------------

    if features.ndim == 2:

        if features.shape[0] != 1:

            raise ValueError(
                "Crop prediction expects one input record."
            )

        features = features[0]

    # -----------------------------------------------------
    # Validate number of features
    # -----------------------------------------------------

    if len(features) != len(
        FEATURE_COLUMNS
    ):

        raise ValueError(
            "Crop prediction requires exactly 7 features: "
            "nitrogen, phosphorus, potassium, "
            "temperature, humidity, ph, rainfall"
        )

    # -----------------------------------------------------
    # Validate values
    # -----------------------------------------------------

    if not np.all(
        np.isfinite(features)
    ):

        raise ValueError(
            "Crop prediction contains invalid numeric values."
        )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    model_data = load_crop_model()

    model = model_data["model"]

    # -----------------------------------------------------
    # Create DataFrame
    # -----------------------------------------------------

    input_data = pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]

    # -----------------------------------------------------
    # Probability
    # -----------------------------------------------------

    probabilities = model.predict_proba(
        input_data
    )[0]

    classes = model.classes_

    best_index = int(
        np.argmax(probabilities)
    )

    confidence = float(
        probabilities[best_index]
    )

    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {
        "recommended_crop": str(
            prediction
        ).strip().lower(),

        "confidence": round(
            confidence * 100,
            2
        ),

        "model": "Random Forest",

        "dataset_records": model_data.get(
            "dataset_records",
            0
        ),

        "crop_classes": len(
            classes
        ),

        "accuracy": round(
            model_data.get(
                "accuracy",
                0
            ) * 100,
            2
        )
    }