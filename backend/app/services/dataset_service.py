from pathlib import Path
import pandas as pd


# =========================================================
# DATASET DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_DIR = BASE_DIR / "dataset"


# =========================================================
# DATASET PATHS
# =========================================================

CROP_DATASET = DATASET_DIR / "crop_data.csv"

SOIL_DATASET = DATASET_DIR / "soil_data_50000.csv"

FERTILIZER_DATASET = DATASET_DIR / "fertilizer_data.csv"

IRRIGATION_DATASET = DATASET_DIR / "irrigation_data.csv"


# =========================================================
# HELPER
# =========================================================

def _load_csv(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_csv(path)


# =========================================================
# CROP DATA
# =========================================================

def load_crop_data():

    data = _load_csv(CROP_DATASET)

    # Your crop dataset uses:
    #
    # N, P, K, temperature, humidity, ph, rainfall, label
    #
    # Convert it to the names expected by the ML model.

    rename_map = {
        "N": "nitrogen",
        "P": "phosphorus",
        "K": "potassium",
        "label": "crop"
    }

    data = data.rename(
        columns=rename_map
    )

    required_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
        "crop"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "Crop dataset is missing columns: "
            + ", ".join(missing)
        )

    return data


# =========================================================
# SOIL DATA
# =========================================================

def load_soil_data():

    data = _load_csv(SOIL_DATASET)

    required_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",
        "moisture",
        "temperature",
        "soil_health"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "Soil dataset is missing columns: "
            + ", ".join(missing)
        )

    # Convert numerical columns safely

    numeric_columns = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",
        "moisture",
        "temperature"
    ]

    for column in numeric_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data["soil_health"] = (
        data["soil_health"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # Remove invalid rows

    data = data.dropna(
        subset=required_columns
    )

    return data


# =========================================================
# FERTILIZER DATA
# =========================================================

def load_fertilizer_data():

    data = _load_csv(
        FERTILIZER_DATASET
    )

    return data


# =========================================================
# IRRIGATION DATA
# =========================================================

def load_irrigation_data():

    data = _load_csv(
        IRRIGATION_DATASET
    )

    return data