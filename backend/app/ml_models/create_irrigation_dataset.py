import pandas as pd

from pathlib import Path


# ---------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "dataset" / "irrigation_data.csv"

OUTPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "integrated_irrigation_data.csv"
)


# ---------------------------------------------------------
# Crop water factors
# ---------------------------------------------------------

CROP_WATER_FACTOR = {
    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25
}


# ---------------------------------------------------------
# Create integrated dataset
# ---------------------------------------------------------

def create_dataset():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # -----------------------------------------------------
    # Crop information
    # -----------------------------------------------------

    crops = [
        "rice",
        "maize",
        "chickpea",
        "cotton",
        "wheat",
        "groundnut",
        "banana"
    ]

    # Repeat crops for the available rows
    df["crop_type"] = [
        crops[i % len(crops)]
        for i in range(len(df))
    ]

    # -----------------------------------------------------
    # Soil nutrient information
    # -----------------------------------------------------

    df["nitrogen"] = [
        40,
        45,
        50,
        55,
        60,
        65,
        70,
        75,
        80,
        85,
        90,
        95,
        100,
        105
    ]

    df["phosphorus"] = [
        20,
        22,
        25,
        28,
        30,
        32,
        35,
        38,
        40,
        42,
        45,
        48,
        50,
        52
    ]

    df["potassium"] = [
        30,
        32,
        35,
        38,
        40,
        42,
        45,
        48,
        50,
        52,
        55,
        58,
        60,
        62
    ]

    # -----------------------------------------------------
    # Soil pH
    # -----------------------------------------------------

    df["ph"] = [
        6.0,
        6.1,
        6.2,
        6.3,
        6.4,
        6.5,
        6.6,
        6.7,
        6.8,
        6.9,
        7.0,
        7.1,
        7.2,
        7.3
    ]

    # -----------------------------------------------------
    # Crop water factor
    # -----------------------------------------------------

    df["crop_water_factor"] = (
        df["crop_type"]
        .map(CROP_WATER_FACTOR)
    )

    # -----------------------------------------------------
    # Select final columns
    # -----------------------------------------------------

    final_columns = [

        "soil_moisture",
        "humidity",
        "temperature",
        "rainfall",
        "soil_temperature",
        "wind_speed",
        "rain_forecast",

        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",

        "crop_type",
        "crop_water_factor",

        "irrigation_recommendation",
        "advice"
    ]

    df = df[final_columns]

    # -----------------------------------------------------
    # Save dataset
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Integrated irrigation dataset created:"
    )

    print(OUTPUT_FILE)

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print("\nColumns:")

    for column in df.columns:
        print(f"- {column}")


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    create_dataset()