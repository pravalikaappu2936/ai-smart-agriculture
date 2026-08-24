import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.services.dataset_service import load_soil_data


# =========================================================
# PATH
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
    # Remove missing values
    # -----------------------------------------------------

    df = df[
        required_columns
    ].dropna()

    # -----------------------------------------------------
    # Features / target
    # -----------------------------------------------------

    X = df[FEATURES]

    y = df[TARGET]

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

        random_state=42,

        class_weight="balanced",

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
    # Prediction
    # -----------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    # -----------------------------------------------------
    # Accuracy
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    # -----------------------------------------------------
    # Classification report
    # -----------------------------------------------------

    report = classification_report(
        y_test,
        y_pred
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH
    )

    # -----------------------------------------------------
    # Console output
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

    print()
    print("CLASSIFICATION REPORT")
    print("-" * 50)

    print(report)

    print("=" * 50)

    return model, accuracy


# =========================================================
# LOAD SAVED MODEL
# =========================================================

def load_soil_model():

    if not os.path.exists(
        MODEL_PATH
    ):

        model, _ = train_soil_model()

        return model

    return joblib.load(
        MODEL_PATH
    )


# =========================================================
# PREDICT SOIL HEALTH
# =========================================================

def predict_soil(features):

    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    model = load_soil_model()

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not features:

        raise ValueError(
            "Soil feature data cannot be empty."
        )

    if len(features[0]) != len(FEATURES):

        raise ValueError(
            f"Expected {len(FEATURES)} features, "
            f"received {len(features[0])}."
        )

    # -----------------------------------------------------
    # IMPORTANT:
    # Use DataFrame with the same feature names used
    # during model training.
    # This removes sklearn feature-name warnings.
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

    probabilities_array = (
        model.predict_proba(
            input_data
        )[0]
    )

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

    confidence = max(
        probabilities_array
    ) * 100

    # -----------------------------------------------------
    # Accuracy
    # -----------------------------------------------------

    # Calculate accuracy from dataset/model
    # without retraining unnecessarily.

    df = load_soil_data()

    X = df[FEATURES]

    y = df[TARGET]

    _, X_test, _, y_test = train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42,

        stratify=y
    )

    test_predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        test_predictions
    )

    # -----------------------------------------------------
    # Return complete result
    # -----------------------------------------------------

    return {

        "soil_health":
            soil_health,

        "accuracy":
            round(
                float(accuracy),
                4
            ),

        "confidence":
            round(
                float(confidence),
                2
            ),

        "probabilities":
            probabilities,

        # Needed by SHAP
        "model":
            model
    }