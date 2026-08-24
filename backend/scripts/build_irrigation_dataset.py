import os
import requests
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

HISTORICAL_DIR = os.path.join(
    DATASET_DIR,
    "historical",
    "weather"
)

PROCESSED_DIR = os.path.join(
    DATASET_DIR,
    "processed"
)


os.makedirs(
    HISTORICAL_DIR,
    exist_ok=True
)

os.makedirs(
    PROCESSED_DIR,
    exist_ok=True
)


# ============================================================
# LOCATION
# ============================================================

# Bengaluru / Karnataka region
#
# You can later change this to your actual farm coordinates.

LATITUDE = 12.9716
LONGITUDE = 77.5946


# ============================================================
# DATE RANGE
# ============================================================

START_DATE = "2020-01-01"
END_DATE = "2025-12-31"


# ============================================================
# OPEN-METEO HISTORICAL API
# ============================================================

API_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


# ============================================================
# WEATHER VARIABLES
# ============================================================

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "et0_fao_evapotranspiration",
    "vapour_pressure_deficit",
    "soil_temperature_0_to_7cm",
    "soil_moisture_0_to_7cm",
    "soil_moisture_7_to_28cm",
]


# ============================================================
# DOWNLOAD HISTORICAL WEATHER
# ============================================================

def download_weather_data():

    print("=" * 60)
    print("DOWNLOADING HISTORICAL WEATHER DATA")
    print("=" * 60)

    params = {

        "latitude":
            LATITUDE,

        "longitude":
            LONGITUDE,

        "start_date":
            START_DATE,

        "end_date":
            END_DATE,

        "hourly":
            ",".join(HOURLY_VARIABLES),

        "timezone":
            "Asia/Kolkata",

        "wind_speed_unit":
            "ms",

        "precipitation_unit":
            "mm",

        "temperature_unit":
            "celsius",

    }


    print(
        f"Location: {LATITUDE}, {LONGITUDE}"
    )

    print(
        f"Period: {START_DATE} → {END_DATE}"
    )


    response = requests.get(
        API_URL,
        params=params,
        timeout=120
    )


    response.raise_for_status()


    data = response.json()


    if "hourly" not in data:

        raise RuntimeError(
            "Historical weather API did not return hourly data."
        )


    hourly = data["hourly"]


    dataframe = pd.DataFrame(hourly)


    output_file = os.path.join(
        HISTORICAL_DIR,
        "historical_weather_raw.csv"
    )


    dataframe.to_csv(
        output_file,
        index=False
    )


    print()
    print(
        f"Downloaded {len(dataframe)} hourly records."
    )

    print(
        f"Saved to: {output_file}"
    )


    return dataframe


# ============================================================
# CLEAN WEATHER DATA
# ============================================================

def clean_weather_data(dataframe):

    print()
    print("=" * 60)
    print("CLEANING WEATHER DATA")
    print("=" * 60)


    dataframe = dataframe.copy()


    # --------------------------------------------------------
    # Convert time
    # --------------------------------------------------------

    dataframe["time"] = pd.to_datetime(
        dataframe["time"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # Remove invalid timestamps
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        subset=["time"]
    )


    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    dataframe = dataframe.sort_values(
        "time"
    )


    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [

        "temperature_2m",

        "relative_humidity_2m",

        "precipitation",

        "rain",

        "wind_speed_10m",

        "et0_fao_evapotranspiration",

        "vapour_pressure_deficit",

        "soil_temperature_0_to_7cm",

        "soil_moisture_0_to_7cm",

        "soil_moisture_7_to_28cm",

    ]


    for column in numeric_columns:

        if column in dataframe.columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )


    # --------------------------------------------------------
    # Fill short missing periods
    # --------------------------------------------------------

    dataframe[numeric_columns] = (
        dataframe[numeric_columns]
        .interpolate(
            method="linear",
            limit_direction="both"
        )
    )


    # --------------------------------------------------------
    # Remove remaining incomplete rows
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        subset=numeric_columns
    )


    print(
        f"Clean records: {len(dataframe)}"
    )


    return dataframe


# ============================================================
# CREATE AGRICULTURAL FEATURES
# ============================================================

def create_features(dataframe):

    print()
    print("=" * 60)
    print("CREATING IRRIGATION FEATURES")
    print("=" * 60)


    dataframe = dataframe.copy()


    # --------------------------------------------------------
    # Time features
    # --------------------------------------------------------

    dataframe["hour"] = (
        dataframe["time"].dt.hour
    )

    dataframe["day_of_year"] = (
        dataframe["time"].dt.dayofyear
    )

    dataframe["month"] = (
        dataframe["time"].dt.month
    )


    # --------------------------------------------------------
    # Rainfall history
    # --------------------------------------------------------

    dataframe["rainfall_6h"] = (
        dataframe["rain"]
        .rolling(
            window=6,
            min_periods=1
        )
        .sum()
    )


    dataframe["rainfall_24h"] = (
        dataframe["rain"]
        .rolling(
            window=24,
            min_periods=1
        )
        .sum()
    )


    dataframe["rainfall_72h"] = (
        dataframe["rain"]
        .rolling(
            window=72,
            min_periods=1
        )
        .sum()
    )


    # --------------------------------------------------------
    # Temperature rolling average
    # --------------------------------------------------------

    dataframe["temperature_6h_avg"] = (
        dataframe["temperature_2m"]
        .rolling(
            window=6,
            min_periods=1
        )
        .mean()
    )


    dataframe["temperature_24h_avg"] = (
        dataframe["temperature_2m"]
        .rolling(
            window=24,
            min_periods=1
        )
        .mean()
    )


    # --------------------------------------------------------
    # Humidity rolling average
    # --------------------------------------------------------

    dataframe["humidity_24h_avg"] = (
        dataframe["relative_humidity_2m"]
        .rolling(
            window=24,
            min_periods=1
        )
        .mean()
    )


    # --------------------------------------------------------
    # ET0 rolling total
    # --------------------------------------------------------

    dataframe["et0_24h"] = (
        dataframe["et0_fao_evapotranspiration"]
        .rolling(
            window=24,
            min_periods=1
        )
        .sum()
    )


    # --------------------------------------------------------
    # Soil moisture conversion
    #
    # Open-Meteo soil moisture is volumetric
    # m³/m³.
    #
    # Convert approximately to percentage.
    # --------------------------------------------------------

    dataframe["soil_moisture_percent"] = (
        dataframe[
            "soil_moisture_0_to_7cm"
        ] * 100
    )


    dataframe["soil_moisture_deep_percent"] = (
        dataframe[
            "soil_moisture_7_to_28cm"
        ] * 100
    )


    # --------------------------------------------------------
    # Soil moisture average
    # --------------------------------------------------------

    dataframe["soil_moisture_avg"] = (

        dataframe[
            "soil_moisture_percent"
        ]

        +

        dataframe[
            "soil_moisture_deep_percent"
        ]

    ) / 2


    # --------------------------------------------------------
    # Water stress indicator
    # --------------------------------------------------------

    dataframe["water_stress"] = (

        dataframe["et0_24h"]

        *

        (
            1
            -
            dataframe["soil_moisture_avg"]
            / 100
        )

    )


    # --------------------------------------------------------
    # Rainfall protection factor
    #
    # Recent rainfall reduces irrigation demand.
    # --------------------------------------------------------

    dataframe["rainfall_factor"] = np.maximum(

        0,

        1
        -
        dataframe["rainfall_24h"]
        / 20

    )


    # --------------------------------------------------------
    # Irrigation demand score
    #
    # This is an initial scientifically-inspired
    # proxy target.
    #
    # Later we should replace this target with
    # actual irrigation records from your farm.
    # --------------------------------------------------------

    dataframe["irrigation_score"] = (

        dataframe["et0_24h"]

        *

        (
            1
            -
            dataframe["soil_moisture_avg"]
            / 100
        )

        *

        dataframe["rainfall_factor"]

    )


    # --------------------------------------------------------
    # Limit score to practical range
    # --------------------------------------------------------

    dataframe["irrigation_score"] = (
        dataframe["irrigation_score"]
        .clip(
            lower=0,
            upper=25
        )
    )


    # --------------------------------------------------------
    # Create recommendation classes
    # --------------------------------------------------------

    dataframe["irrigation_recommendation"] = (

        pd.cut(

            dataframe["irrigation_score"],

            bins=[
                -np.inf,
                1,
                3,
                6,
                np.inf
            ],

            labels=[
                "No irrigation",
                "Monitor",
                "Irrigate soon",
                "Irrigate now"
            ]

        )

    )


    return dataframe


# ============================================================
# FINALIZE DATASET
# ============================================================

def finalize_dataset(dataframe):

    print()
    print("=" * 60)
    print("CREATING FINAL TRAINING DATASET")
    print("=" * 60)


    feature_columns = [

        "temperature_2m",

        "relative_humidity_2m",

        "rain",

        "wind_speed_10m",

        "soil_temperature_0_to_7cm",

        "soil_moisture_percent",

        "soil_moisture_deep_percent",

        "soil_moisture_avg",

        "rainfall_6h",

        "rainfall_24h",

        "rainfall_72h",

        "temperature_6h_avg",

        "temperature_24h_avg",

        "humidity_24h_avg",

        "et0_24h",

        "vapour_pressure_deficit",

        "water_stress",

        "rainfall_factor",

        "hour",

        "day_of_year",

        "month",

        "irrigation_score",

        "irrigation_recommendation",

    ]


    final_data = dataframe[
        feature_columns
    ].copy()


    output_file = os.path.join(
        PROCESSED_DIR,
        "improved_irrigation_training_data.csv"
    )


    final_data.to_csv(
        output_file,
        index=False
    )


    print()
    print(
        f"Final dataset rows: {len(final_data)}"
    )

    print(
        f"Final dataset columns: {len(final_data.columns)}"
    )

    print(
        f"Saved to: {output_file}"
    )


    print()
    print("Recommendation distribution:")

    print(
        final_data[
            "irrigation_recommendation"
        ]
        .value_counts()
    )


    return final_data


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("AI SMART AGRICULTURE")
    print("IMPROVED IRRIGATION DATASET BUILDER")
    print("=" * 60)
    print()


    try:

        # ----------------------------------------------------
        # 1. Download
        # ----------------------------------------------------

        weather_data = (
            download_weather_data()
        )


        # ----------------------------------------------------
        # 2. Clean
        # ----------------------------------------------------

        weather_data = (
            clean_weather_data(
                weather_data
            )
        )


        # ----------------------------------------------------
        # 3. Feature engineering
        # ----------------------------------------------------

        weather_data = (
            create_features(
                weather_data
            )
        )


        # ----------------------------------------------------
        # 4. Final dataset
        # ----------------------------------------------------

        final_data = (
            finalize_dataset(
                weather_data
            )
        )


        print()
        print("=" * 60)
        print("DATASET BUILD COMPLETED SUCCESSFULLY")
        print("=" * 60)


        print()
        print(
            final_data.head()
        )


    except Exception as error:

        print()
        print("=" * 60)
        print("DATASET BUILD FAILED")
        print("=" * 60)

        print(
            f"Error: {error}"
        )


        raise


if __name__ == "__main__":

    main()