from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parents[1]

DATASET_PATH = BACKEND_DIR / "dataset" / "crop_yield_data.csv"

MODEL_DIR = BASE_DIR / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "crop_yield_random_forest.pkl"
METADATA_PATH = MODEL_DIR / "crop_yield_model_metadata.json"


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

TARGET_COLUMN = "yield"

CATEGORICAL_FEATURES = [
    "state",
    "crop",
    "season",
]

NUMERIC_FEATURES = [
    "year",
    "area",
    "annual_rainfall",
    "fertilizer",
    "pesticide",
]


# ============================================================
# DATASET COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {
    "year": [
        "year",
    ],

    "state": [
        "state",
        "state_name",
    ],

    "crop": [
        "crop",
        "crop_name",
    ],

    "season": [
        "season",
    ],

    "area": [
        "area",
        "area_hectares",
        "area_ha",
    ],

    "production": [
        "production",
        "production_tonnes",
        "production_tons",
    ],

    "annual_rainfall": [
        "annual_rainfall",
        "rainfall",
        "rainfall_mm",
    ],

    "fertilizer": [
        "fertilizer",
        "fertilizer_kg",
    ],

    "pesticide": [
        "pesticide",
        "pesticides",
        "pesticide_kg",
    ],

    "yield": [
        "yield",
        "yield_tonnes_per_hectare",
        "yield_ton_per_hectare",
    ],
}


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("=" * 60)
    print("CROP YIELD MODEL TRAINING")
    print("=" * 60)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    if DATASET_PATH.stat().st_size == 0:
        raise ValueError(
            f"Dataset is empty:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise ValueError("Crop yield dataset contains no records.")

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    # Rename aliases
    rename_map = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        for alias in aliases:

            if alias in df.columns:
                rename_map[alias] = standard_name
                break

    df = df.rename(columns=rename_map)

    required_columns = [
        "year",
        "state",
        "crop",
        "season",
        "area",
        "production",
        "annual_rainfall",
        "fertilizer",
        "pesticide",
        "yield",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    print(f"Dataset records loaded: {len(df)}")

    return df


# ============================================================
# CLEAN DATASET
# ============================================================

def clean_dataset(df):

    print("\nCleaning dataset...")

    numeric_columns = [
        "year",
        "area",
        "production",
        "annual_rainfall",
        "fertilizer",
        "pesticide",
        "yield",
    ]

    categorical_columns = [
        "state",
        "crop",
        "season",
    ]

    # Convert numeric columns
    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Clean categorical columns
    for column in categorical_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Remove missing values
    df = df.dropna(
        subset=numeric_columns + categorical_columns
    )

    # Remove invalid values
    df = df[
        (df["year"] >= 2000)
        & (df["year"] <= 2100)
        & (df["area"] > 0)
        & (df["production"] >= 0)
        & (df["annual_rainfall"] >= 0)
        & (df["fertilizer"] >= 0)
        & (df["pesticide"] >= 0)
        & (df["yield"] >= 0)
    ]

    # Remove infinite values
    df = df.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    df = df.dropna()

    # Remove duplicate records
    df = df.drop_duplicates()

    # Reset index
    df = df.reset_index(drop=True)

    print(f"Valid dataset records: {len(df)}")

    print(
        f"Crops: {df['crop'].nunique()}"
    )

    print(
        f"States: {df['state'].nunique()}"
    )

    print(
        f"Seasons: {df['season'].nunique()}"
    )

    if len(df) < 100:

        raise ValueError(
            "Not enough valid records for training."
        )

    return df


# ============================================================
# ENCODE CATEGORICAL FEATURES
# ============================================================

def encode_categories(df):

    print("\nEncoding categorical features...")

    df = df.copy()

    encoders = {}

    for column in CATEGORICAL_FEATURES:

        values = sorted(
            df[column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        encoder = {
            value: index
            for index, value in enumerate(values)
        }

        encoders[column] = encoder

        df[column] = (
            df[column]
            .astype(str)
            .map(encoder)
        )

    return df, encoders


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_features(df):

    # Production is deliberately NOT used as an input.
    #
    # Yield is related to production / area, so using
    # production as a predictor would cause target leakage.

    X = df[FEATURE_NAMES].copy()

    y = df[TARGET_COLUMN].copy()

    return X, y


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    df = load_dataset()

    df = clean_dataset(df)

    encoded_df, encoders = encode_categories(df)

    X, y = prepare_features(encoded_df)

    # Convert to float32 to reduce memory usage
    X = X.astype(np.float32)

    y = y.astype(np.float32)

    print("\nFeatures:")
    for feature in FEATURE_NAMES:
        print(f"  - {feature}")

    print(f"\nTraining records: {len(X)}")

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    print(f"Training set: {len(X_train)}")
    print(f"Testing set : {len(X_test)}")

    # --------------------------------------------------------
    # MEMORY-OPTIMIZED RANDOM FOREST
    # --------------------------------------------------------
    #
    # Dataset is NOT reduced.
    #
    # Optimization is done by reducing model complexity:
    # 80 trees -> 40 trees
    # depth 18 -> 12
    #
    # This is similar to the optimization approach used
    # for the other Random Forest models in the project.

    print("\nTraining memory-optimized Random Forest...")

    model = RandomForestRegressor(
        n_estimators=40,
        max_depth=12,
        min_samples_leaf=2,
        max_features=0.7,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    print("\nEvaluating model...")

    predictions = model.predict(X_test)

    predictions = np.asarray(
        predictions,
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    r2 = r2_score(
        y_test,
        predictions,
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions,
        )
    )

    # --------------------------------------------------------
    # MODEL PACKAGE
    # --------------------------------------------------------

    model_package = {

        "model": model,

        "encoders": encoders,

        "features": FEATURE_NAMES,

        "categorical_features": CATEGORICAL_FEATURES,

        "numeric_features": NUMERIC_FEATURES,

        "target": TARGET_COLUMN,

        "r2": float(r2),

        "mae": float(mae),

        "rmse": float(rmse),

        "dataset_records": int(len(df)),

        "training_records": int(len(X_train)),

        "testing_records": int(len(X_test)),

        "model_parameters": {
            "n_estimators": 40,
            "max_depth": 12,
            "min_samples_leaf": 2,
            "max_features": 0.7,
        },
    }

    # --------------------------------------------------------
    # SAVE COMPRESSED MODEL
    # --------------------------------------------------------

    print("\nSaving compressed model...")

    joblib.dump(
        model_package,
        MODEL_PATH,
        compress=3,
    )

    # --------------------------------------------------------
    # SAVE METADATA
    # --------------------------------------------------------

    metadata = {

        "model": "RandomForestRegressor",

        "dataset_records": int(len(df)),

        "training_records": int(len(X_train)),

        "testing_records": int(len(X_test)),

        "features": FEATURE_NAMES,

        "categorical_features": CATEGORICAL_FEATURES,

        "numeric_features": NUMERIC_FEATURES,

        "target": TARGET_COLUMN,

        "r2": float(r2),

        "mae": float(mae),

        "rmse": float(rmse),

        "model_parameters": {
            "n_estimators": 40,
            "max_depth": 12,
            "min_samples_leaf": 2,
            "max_features": 0.7,
            "random_state": 42,
        },
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    # --------------------------------------------------------
    # FILE SIZE
    # --------------------------------------------------------

    model_size_mb = (
        MODEL_PATH.stat().st_size
        / (1024 * 1024)
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CROP YIELD MODEL TRAINED")
    print("=" * 60)

    print(
        f"Dataset records : {len(df)}"
    )

    print(
        f"Training records: {len(X_train)}"
    )

    print(
        f"Testing records : {len(X_test)}"
    )

    print(
        f"Features        : {len(FEATURE_NAMES)}"
    )

    print(
        f"Crops           : {df['crop'].nunique()}"
    )

    print(
        f"States          : {df['state'].nunique()}"
    )

    print(
        f"Seasons         : {df['season'].nunique()}"
    )

    print(
        f"R²              : {r2:.4f}"
    )

    print(
        f"MAE             : {mae:.4f}"
    )

    print(
        f"RMSE            : {rmse:.4f}"
    )

    print(
        f"Model size      : {model_size_mb:.2f} MB"
    )

    print(
        f"Model           : {MODEL_PATH}"
    )

    print(
        f"Metadata        : {METADATA_PATH}"
    )

    print("=" * 60)


if __name__ == "__main__":
    train_model()