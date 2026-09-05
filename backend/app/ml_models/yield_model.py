from pathlib import Path
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "saved_models"
    / "crop_yield_random_forest.pkl"
)


# ============================================================
# FEATURES
# ============================================================

FEATURE_NAMES = [
    "year",
    "state",
    "crop",
    "season",
    "area",
    "annual_rainfall",
    "fertilizer",
    "pesticide",
]

CATEGORICAL_FEATURES = [
    "state",
    "crop",
    "season",
]


# ============================================================
# LAZY MODEL LOADING
# ============================================================
#
# The model is NOT loaded when FastAPI starts.
#
# It is loaded only when /yield/predict is called.
#
# maxsize=1 ensures only one copy is cached.

@lru_cache(maxsize=1)
def load_yield_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Crop yield model not found: {MODEL_PATH}"
        )

    if MODEL_PATH.stat().st_size == 0:

        raise ValueError(
            "Crop yield model file is empty."
        )

    model_package = joblib.load(
        MODEL_PATH
    )

    if not isinstance(
        model_package,
        dict,
    ):

        raise ValueError(
            "Invalid crop yield model package."
        )

    if "model" not in model_package:

        raise ValueError(
            "Crop yield model is missing."
        )

    if "encoders" not in model_package:

        raise ValueError(
            "Crop yield encoders are missing."
        )

    return model_package


# ============================================================
# ENCODE INPUT
# ============================================================

def _encode_input(
    data: dict,
    package: dict,
) -> pd.DataFrame:

    feature_names = package.get(
        "features",
        FEATURE_NAMES,
    )

    row = {

        "year": float(
            data["year"]
        ),

        "state": str(
            data["state"]
        ).strip(),

        "crop": str(
            data["crop"]
        ).strip(),

        "season": str(
            data["season"]
        ).strip(),

        "area": float(
            data["area"]
        ),

        "annual_rainfall": float(
            data["annual_rainfall"]
        ),

        "fertilizer": float(
            data["fertilizer"]
        ),

        "pesticide": float(
            data["pesticide"]
        ),
    }

    # --------------------------------------------------------
    # Validate numeric values
    # --------------------------------------------------------

    numeric_values = [
        row["year"],
        row["area"],
        row["annual_rainfall"],
        row["fertilizer"],
        row["pesticide"],
    ]

    if not np.isfinite(
        np.asarray(
            numeric_values,
            dtype=np.float32,
        )
    ).all():

        raise ValueError(
            "Crop yield input contains invalid numeric values."
        )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(
        [row]
    )

    encoders = package.get(
        "encoders",
        {},
    )

    # --------------------------------------------------------
    # Encode categorical values
    # --------------------------------------------------------

    for column in CATEGORICAL_FEATURES:

        encoder = encoders.get(
            column
        )

        if encoder is None:

            raise ValueError(
                f"Encoder for '{column}' is missing."
            )

        value = row[column]

        if value not in encoder:

            raise ValueError(
                f"Unknown {column}: {value}"
            )

        df[column] = encoder[value]

    # --------------------------------------------------------
    # Return exact feature order
    # --------------------------------------------------------

    return df[
        feature_names
    ].astype(
        np.float32
    )


# ============================================================
# PREDICT YIELD
# ============================================================

def predict_yield(
    data: dict,
) -> dict:

    package = load_yield_model()

    model = package["model"]

    input_df = _encode_input(
        data,
        package,
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model.predict(
        input_df
    )[0]

    prediction = float(
        prediction
    )

    if not np.isfinite(
        prediction
    ):

        raise ValueError(
            "Crop yield model returned an invalid prediction."
        )

    # Yield cannot be negative
    prediction = max(
        0.0,
        prediction,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    r2 = float(
        package.get(
            "r2",
            0.0,
        )
    )

    mae = float(
        package.get(
            "mae",
            0.0,
        )
    )

    rmse = float(
        package.get(
            "rmse",
            0.0,
        )
    )

    dataset_records = int(
        package.get(
            "dataset_records",
            0,
        )
    )

    # --------------------------------------------------------
    # Yield category
    # --------------------------------------------------------

    if prediction < 2:

        category = "Low"

    elif prediction < 5:

        category = "Moderate"

    else:

        category = "High"

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "predicted_yield": round(
            prediction,
            3,
        ),

        "unit": "tonnes/hectare",

        "yield_category": category,

        "r2": round(
            r2,
            4,
        ),

        "mae": round(
            mae,
            4,
        ),

        "rmse": round(
            rmse,
            4,
        ),

        "dataset_records": dataset_records,
    }