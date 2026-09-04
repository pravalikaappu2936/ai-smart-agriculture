import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_fertilizer_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = (
    BASE_DIR / "saved_models"
)

MODEL_PATH = (
    MODEL_DIR /
    "fertilizer_random_forest.pkl"
)

METADATA_PATH = (
    MODEL_DIR /
    "fertilizer_model_metadata.json"
)


# =========================================================
# FEATURE NAMES
# =========================================================

FEATURE_NAMES = [

    "nitrogen",

    "phosphorus",

    "potassium",

    "ph",

    "moisture",

    "temperature"

]


# =========================================================
# CACHED MODEL
# =========================================================

_FERTILIZER_MODEL = None


# =========================================================
# PREPARE DATASET
# =========================================================

def prepare_fertilizer_data():

    dataset = load_fertilizer_data()

    if dataset is None or dataset.empty:

        raise ValueError(
            "Fertilizer dataset is empty."
        )

    # -----------------------------------------------------
    # Required columns
    # -----------------------------------------------------

    required_columns = [

        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",
        "moisture",
        "temperature",
        "recommended_fertilizer"

    ]

    # -----------------------------------------------------
    # Check columns
    # -----------------------------------------------------

    missing_columns = [

        column
        for column in required_columns
        if column not in dataset.columns

    ]

    if missing_columns:

        raise ValueError(
            "Fertilizer dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    # -----------------------------------------------------
    # Copy dataset
    # -----------------------------------------------------

    dataset = dataset.copy()

    # -----------------------------------------------------
    # Convert numeric columns
    # -----------------------------------------------------

    for column in FEATURE_NAMES:

        dataset[column] = pd.to_numeric(
            dataset[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean fertilizer labels
    # -----------------------------------------------------

    dataset[
        "recommended_fertilizer"
    ] = (

        dataset[
            "recommended_fertilizer"
        ]

        .astype(str)

        .str.strip()

    )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    dataset = dataset.dropna(
        subset=FEATURE_NAMES
    )

    dataset = dataset[
        dataset[
            "recommended_fertilizer"
        ] != ""
    ]

    # -----------------------------------------------------
    # Validate dataset
    # -----------------------------------------------------

    if len(dataset) < 2:

        raise ValueError(
            "Not enough valid fertilizer "
            "dataset records."
        )

    # -----------------------------------------------------
    # X
    # -----------------------------------------------------

    X = dataset[
        FEATURE_NAMES
    ].astype(float)

    # -----------------------------------------------------
    # y
    # -----------------------------------------------------

    y = dataset[
        "recommended_fertilizer"
    ]

    # -----------------------------------------------------
    # Validate classes
    # -----------------------------------------------------

    if y.nunique() < 2:

        raise ValueError(
            "Fertilizer dataset must contain "
            "at least two different classes."
        )

    return X, y


# =========================================================
# TRAIN MODEL
# =========================================================

def train_fertilizer_model():

    X, y = prepare_fertilizer_data()

    # -----------------------------------------------------
    # Train/test split
    # -----------------------------------------------------

    class_counts = y.value_counts()

    use_stratify = (
        class_counts.min() >= 2
    )

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.25,

        random_state=42,

        stratify=y if use_stratify else None

    )

    # -----------------------------------------------------
    # Random Forest
    #
    # Reduced from 200 trees to 100 trees
    # to reduce model size and RAM usage.
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=100,

        random_state=42,

        class_weight="balanced",

        min_samples_leaf=1,

        n_jobs=-1

    )

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Test
    # -----------------------------------------------------

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    # -----------------------------------------------------
    # Save directory
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
        compress=3
    )

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    metadata = {

        "accuracy":
            float(accuracy),

        "dataset_records":
            int(len(X)),

        "features":
            FEATURE_NAMES,

        "classes":
            sorted(
                y.unique().tolist()
            )

    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print()
    print("=" * 50)
    print("FERTILIZER MODEL TRAINED")
    print("=" * 50)

    print(
        f"Dataset records : {len(X)}"
    )

    print(
        f"Features        : {len(FEATURE_NAMES)}"
    )

    print(
        f"Classes         : {len(y.unique())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print("=" * 50)

    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_fertilizer_model():

    global _FERTILIZER_MODEL

    # -----------------------------------------------------
    # Return cached model
    # -----------------------------------------------------

    if _FERTILIZER_MODEL is not None:

        return _FERTILIZER_MODEL

    # -----------------------------------------------------
    # Model must already exist
    # -----------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            "Saved fertilizer model not found: "
            f"{MODEL_PATH}. "

            "Train the model locally before deployment."

        )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    try:

        print(
            "Loading fertilizer model..."
        )

        _FERTILIZER_MODEL = joblib.load(
            MODEL_PATH
        )

        print(
            "Fertilizer model loaded successfully."
        )

        return _FERTILIZER_MODEL

    except Exception as error:

        print(
            "Unable to load fertilizer model."
        )

        print(
            f"Reason: {error}"
        )

        raise RuntimeError(
            "Fertilizer model could not be loaded."
        ) from error


# =========================================================
# LOAD MODEL ACCURACY
# =========================================================

def load_fertilizer_accuracy():

    if not METADATA_PATH.exists():

        return 0.0

    try:

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metadata = json.load(file)

        return float(
            metadata.get(
                "accuracy",
                0.0
            )
        )

    except Exception as error:

        print(
            "Unable to load fertilizer metadata:",
            error
        )

        return 0.0


# =========================================================
# PREDICT FERTILIZER
# =========================================================

def predict_fertilizer(features):

    # -----------------------------------------------------
    # Convert input
    # -----------------------------------------------------

    features = np.asarray(
        features,
        dtype=np.float32
    )

    # -----------------------------------------------------
    # Make 2D
    # -----------------------------------------------------

    if features.ndim == 1:

        features = features.reshape(
            1,
            -1
        )

    # -----------------------------------------------------
    # Validate dimensions
    # -----------------------------------------------------

    if features.ndim != 2:

        raise ValueError(
            "Fertilizer input must contain "
            "one or more rows of features."
        )

    if features.shape[1] != len(
        FEATURE_NAMES
    ):

        raise ValueError(

            f"Expected "
            f"{len(FEATURE_NAMES)} "
            f"fertilizer features, "

            f"received "
            f"{features.shape[1]}."

        )

    # -----------------------------------------------------
    # Validate numeric values
    # -----------------------------------------------------

    if not np.all(
        np.isfinite(features)
    ):

        raise ValueError(
            "Fertilizer input contains "
            "invalid numeric values."
        )

    # -----------------------------------------------------
    # Load cached model
    # -----------------------------------------------------

    model = load_fertilizer_model()

    # -----------------------------------------------------
    # Create DataFrame
    # -----------------------------------------------------

    features_df = pd.DataFrame(

        features,

        columns=FEATURE_NAMES

    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = model.predict(
        features_df
    )[0]

    # -----------------------------------------------------
    # Accuracy
    #
    # Read saved accuracy instead of
    # retraining/retesting the model.
    # -----------------------------------------------------

    accuracy = load_fertilizer_accuracy()

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    confidence = 0.0

    if hasattr(
        model,
        "predict_proba"
    ):

        probabilities = model.predict_proba(
            features_df
        )[0]

        confidence = (
            float(
                np.max(probabilities)
            ) * 100
        )

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "fertilizer":
            str(prediction),

        "accuracy":
            round(
                accuracy * 100,
                2
            ),

        "confidence":
            round(
                confidence,
                2
            )

    }