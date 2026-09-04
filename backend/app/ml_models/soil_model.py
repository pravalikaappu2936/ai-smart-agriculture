import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import load_soil_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "saved_models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "soil_random_forest.pkl"
)

ACCURACY_PATH = os.path.join(
    MODEL_DIR,
    "soil_model_accuracy.txt"
)


# =========================================================
# FEATURES
# =========================================================

FEATURES = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "moisture",
    "temperature"
]

TARGET = "soil_health"


# =========================================================
# CACHED MODEL
# =========================================================

_SOIL_MODEL = None


# =========================================================
# TRAIN SOIL MODEL
# =========================================================

def train_soil_model():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Load dataset
    # -----------------------------------------------------

    df = load_soil_data()

    if df is None or df.empty:
        raise ValueError(
            "Soil dataset is empty."
        )

    # -----------------------------------------------------
    # Validate columns
    # -----------------------------------------------------

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Soil dataset is missing columns: "
            f"{missing_columns}"
        )

    # -----------------------------------------------------
    # Keep required columns only
    # -----------------------------------------------------

    df = df[
        required_columns
    ].copy()

    # -----------------------------------------------------
    # Convert numerical columns
    # -----------------------------------------------------

    for column in FEATURES:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Clean target
    # -----------------------------------------------------

    df[TARGET] = (
        df[TARGET]
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # Remove invalid rows
    # -----------------------------------------------------

    df = df.dropna(
        subset=FEATURES + [TARGET]
    )

    df = df[
        df[TARGET] != ""
    ]

    if df.empty:
        raise ValueError(
            "No valid soil records available."
        )

    # -----------------------------------------------------
    # X and y
    # -----------------------------------------------------

    X = df[
        FEATURES
    ].astype(float)

    y = df[
        TARGET
    ]

    # -----------------------------------------------------
    # Check classes
    # -----------------------------------------------------

    if y.nunique() < 2:
        raise ValueError(
            "Soil dataset must contain "
            "at least two classes."
        )

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
    # OPTIMIZED RANDOM FOREST
    # -----------------------------------------------------

    model = RandomForestClassifier(

        # Reduced from 300
        n_estimators=100,

        random_state=42,

        class_weight="balanced",

        # Helps reduce unnecessary tree growth
        min_samples_leaf=1,

        n_jobs=-1
    )

    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    print()
    print("=" * 50)
    print("TRAINING SOIL MODEL")
    print("=" * 50)

    print(
        f"Dataset records : {len(df)}"
    )

    print(
        f"Features        : {len(FEATURES)}"
    )

    print(
        f"Classes         : {sorted(y.unique().tolist())}"
    )

    print(
        "Random Forest trees : 100"
    )

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Evaluate
    # -----------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    # -----------------------------------------------------
    # Save model with compression
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
        compress=3
    )

    # -----------------------------------------------------
    # Save accuracy separately
    # -----------------------------------------------------

    with open(
        ACCURACY_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            str(float(accuracy))
        )

    # -----------------------------------------------------
    # Clear cached model
    # -----------------------------------------------------

    global _SOIL_MODEL

    _SOIL_MODEL = model

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    print()
    print("=" * 50)
    print("SOIL MODEL TRAINED")
    print("=" * 50)

    print(
        f"Dataset records : {len(df)}"
    )

    print(
        f"Features        : {len(FEATURES)}"
    )

    print(
        f"Classes         : {sorted(y.unique().tolist())}"
    )

    print(
        f"Accuracy        : {accuracy * 100:.2f}%"
    )

    print(
        f"Model saved     : {MODEL_PATH}"
    )

    print(
        f"Model size      : "
        f"{os.path.getsize(MODEL_PATH) / (1024 * 1024):.2f} MB"
    )

    print("=" * 50)

    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_soil_model():

    global _SOIL_MODEL

    # -----------------------------------------------------
    # Reuse model already loaded in memory
    # -----------------------------------------------------

    if _SOIL_MODEL is not None:
        return _SOIL_MODEL

    # -----------------------------------------------------
    # Model must already exist
    # -----------------------------------------------------

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"Soil model not found: {MODEL_PATH}"
        )

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    try:

        print(
            "Loading soil model..."
        )

        _SOIL_MODEL = joblib.load(
            MODEL_PATH
        )

        print(
            "Soil model loaded successfully."
        )

        return _SOIL_MODEL

    except Exception as error:

        print(
            "Unable to load soil model."
        )

        print(
            f"Reason: {error}"
        )

        raise RuntimeError(
            "Soil model could not be loaded."
        ) from error


# =========================================================
# LOAD SAVED ACCURACY
# =========================================================

def load_soil_accuracy():

    if not os.path.exists(
        ACCURACY_PATH
    ):

        return 0.0

    try:

        with open(
            ACCURACY_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return float(
                file.read().strip()
            )

    except Exception:

        return 0.0


# =========================================================
# PREDICT SOIL HEALTH
# =========================================================

def predict_soil(features):

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if features is None:

        raise ValueError(
            "Soil feature data cannot be empty."
        )

    # -----------------------------------------------------
    # Convert to NumPy
    # -----------------------------------------------------

    features = np.asarray(
        features,
        dtype=float
    )

    # -----------------------------------------------------
    # Make sure input is 2D
    # -----------------------------------------------------

    if features.ndim == 1:

        features = features.reshape(
            1,
            -1
        )

    if features.ndim != 2:

        raise ValueError(
            "Soil input must be a 2D feature array."
        )

    # -----------------------------------------------------
    # Only one record expected
    # -----------------------------------------------------

    if features.shape[0] != 1:

        raise ValueError(
            "Soil prediction expects one input record."
        )

    # -----------------------------------------------------
    # Validate feature count
    # -----------------------------------------------------

    if features.shape[1] != len(FEATURES):

        raise ValueError(
            f"Expected {len(FEATURES)} features, "
            f"received {features.shape[1]}."
        )

    # -----------------------------------------------------
    # Validate numeric values
    # -----------------------------------------------------

    if not np.all(
        np.isfinite(features)
    ):

        raise ValueError(
            "Soil input contains invalid numeric values."
        )

    # -----------------------------------------------------
    # Load cached model
    # -----------------------------------------------------

    model = load_soil_model()

    # -----------------------------------------------------
    # DataFrame with feature names
    # -----------------------------------------------------

    input_data = pd.DataFrame(
        features,
        columns=FEATURES
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction = model.predict(
        input_data
    )

    soil_health = str(
        prediction[0]
    )

    # -----------------------------------------------------
    # Probabilities
    # -----------------------------------------------------

    probabilities_array = model.predict_proba(
        input_data
    )[0]

    probabilities = {}

    for class_name, probability in zip(
        model.classes_,
        probabilities_array
    ):

        probabilities[
            str(class_name)
        ] = round(
            float(probability) * 100,
            2
        )

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    confidence = (
        float(
            np.max(
                probabilities_array
            )
        ) * 100
    )

    # -----------------------------------------------------
    # Load saved accuracy
    # -----------------------------------------------------

    accuracy = load_soil_accuracy()

    # -----------------------------------------------------
    # Return
    # -----------------------------------------------------

    return {

        "soil_health":
            soil_health,

        "accuracy":
            round(
                accuracy,
                4
            ),

        "confidence":
            round(
                confidence,
                2
            ),

        "probabilities":
            probabilities,

        # Required by SHAP
        "model":
            model
    }