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
# MODEL PATH
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
# CACHED MODEL
# =========================================================

_CROP_MODEL = None


# =========================================================
# TRAIN MODEL
# =========================================================

def train_crop_model():
    """
    Train the Random Forest crop recommendation model.

    Training should be performed locally.
    The trained model is then deployed to Render.
    """

    dataset = load_crop_data()

    if dataset is None or dataset.empty:
        raise ValueError(
            "Crop dataset is empty."
        )

    # -----------------------------------------------------
    # Check required columns
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
    #
    # Reduced from 100 trees to 75 trees.
    #
    # This reduces RAM and model size while still
    # providing good classification performance.
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=75,

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
    # Model information
    # -----------------------------------------------------

    model_data = {

        "model":
            model,

        "features":
            FEATURE_COLUMNS,

        "accuracy":
            float(accuracy),

        "dataset_records":
            int(len(dataset)),

        "crop_classes":
            sorted(
                y.unique().tolist()
            )

    }

    # -----------------------------------------------------
    # Save compressed model
    # -----------------------------------------------------

    joblib.dump(

        model_data,

        MODEL_PATH,

        compress=3

    )

    # -----------------------------------------------------
    # Console output
    # -----------------------------------------------------

    print()
    print("=" * 50)
    print("CROP MODEL TRAINED")
    print("=" * 50)

    print(
        f"Dataset records : {len(dataset)}"
    )

    print(
        f"Features        : {len(FEATURE_COLUMNS)}"
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

    print("=" * 50)

    return model_data


# =========================================================
# LOAD MODEL
# =========================================================

def load_crop_model():
    """
    Load the trained crop model once and reuse it.

    The model is NOT retrained automatically.
    This prevents large memory usage on Render.
    """

    global _CROP_MODEL

    # -----------------------------------------------------
    # Return cached model
    # -----------------------------------------------------

    if _CROP_MODEL is not None:
        return _CROP_MODEL

    # -----------------------------------------------------
    # Model must already exist
    # -----------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            f"Crop model not found: {MODEL_PATH}. "

            "Train the model locally before deployment."

        )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    try:

        print(
            "Loading crop model..."
        )

        _CROP_MODEL = joblib.load(
            MODEL_PATH
        )

        print(
            "Crop model loaded successfully."
        )

        return _CROP_MODEL

    except Exception as error:

        print(
            "Unable to load crop model."
        )

        print(
            f"Reason: {error}"
        )

        raise RuntimeError(

            "Crop model could not be loaded."

        ) from error


# =========================================================
# PREDICT CROP
# =========================================================

def predict_crop(features):
    """
    Predict the most suitable crop.

    Expected features:

    nitrogen
    phosphorus
    potassium
    temperature
    humidity
    ph
    rainfall
    """

    # -----------------------------------------------------
    # Convert input
    # -----------------------------------------------------

    features = np.asarray(
        features,
        dtype=np.float32
    )

    # -----------------------------------------------------
    # Handle 2D input
    # -----------------------------------------------------

    if features.ndim == 2:

        if features.shape[0] != 1:

            raise ValueError(
                "Crop prediction expects "
                "one input record."
            )

        features = features[0]

    # -----------------------------------------------------
    # Validate dimensions
    # -----------------------------------------------------

    if features.ndim != 1:

        raise ValueError(
            "Crop prediction input must "
            "be a one-dimensional feature list."
        )

    if len(features) != len(
        FEATURE_COLUMNS
    ):

        raise ValueError(

            "Crop prediction requires exactly "
            "7 features: "

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
            "Crop prediction contains "
            "invalid numeric values."
        )

    # -----------------------------------------------------
    # Load cached model
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

        "recommended_crop":
            str(
                prediction
            ).strip().lower(),

        "confidence":
            round(
                confidence * 100,
                2
            ),

        "model":
            "Random Forest",

        "dataset_records":
            model_data.get(
                "dataset_records",
                0
            ),

        "crop_classes":
            len(
                model.classes_
            ),

        "accuracy":
            round(
                model_data.get(
                    "accuracy",
                    0
                ) * 100,
                2
            )

    }