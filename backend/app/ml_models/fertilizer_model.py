import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.dataset_service import (
    load_fertilizer_data
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
# PREPARE DATASET
# =========================================================

def prepare_fertilizer_data():

    dataset = load_fertilizer_data()


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

    for column in required_columns:

        if column not in dataset.columns:

            raise ValueError(

                f"Column '{column}' not found "
                "in fertilizer dataset."

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
    # Check dataset
    # -----------------------------------------------------

    if len(dataset) < 2:

        raise ValueError(

            "Not enough valid fertilizer "
            "dataset records to train the model."

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
    # Check classes
    # -----------------------------------------------------

    if y.nunique() < 2:

        raise ValueError(

            "Fertilizer dataset must contain "
            "at least two different fertilizer classes."

        )


    return X, y


# =========================================================
# TRAIN MODEL
# =========================================================

def train_fertilizer_model():

    X, y = prepare_fertilizer_data()


    # -----------------------------------------------------
    # Stratification
    # -----------------------------------------------------

    class_counts = y.value_counts()

    use_stratify = (
        class_counts.min() >= 2
    )


    # -----------------------------------------------------
    # Split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.25,

        random_state=42,

        stratify=y if use_stratify else None

    )


    # -----------------------------------------------------
    # Random Forest
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=200,

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


    return model, accuracy


# =========================================================
# PREDICT FERTILIZER
# =========================================================

def predict_fertilizer(features):

    # -----------------------------------------------------
    # Train model
    # -----------------------------------------------------

    model, accuracy = train_fertilizer_model()


    # -----------------------------------------------------
    # Convert input
    # -----------------------------------------------------

    features = np.asarray(

        features,

        dtype=float

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
    # Validate number of features
    # -----------------------------------------------------

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
    # DataFrame
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
    # Result
    # -----------------------------------------------------

    return {

        "fertilizer":
            str(prediction),

        "accuracy":
            round(

                float(accuracy) * 100,

                2

            )

    }