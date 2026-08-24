# =========================================================
# IRRIGATION MODEL
# Dataset + Crop + Soil Moisture + Weather + Random Forest
# =========================================================

from pathlib import Path

import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml_models"
    / "irrigation_model.pkl"
)

SCALER_PATH = (
    BASE_DIR
    / "app"
    / "ml_models"
    / "irrigation_scaler.pkl"
)


# =========================================================
# LOAD TRAINED MODEL
# =========================================================

model = None
scaler = None


try:

    if MODEL_PATH.exists():

        model = joblib.load(
            MODEL_PATH
        )

        print(
            "Irrigation model loaded successfully."
        )

    else:

        print(
            "Warning: irrigation_model.pkl not found."
        )

except Exception as exc:

    print(
        "Warning: irrigation model could not be loaded:",
        exc
    )


try:

    if SCALER_PATH.exists():

        scaler = joblib.load(
            SCALER_PATH
        )

        print(
            "Irrigation scaler loaded successfully."
        )

    else:

        print(
            "Warning: irrigation_scaler.pkl not found."
        )

except Exception as exc:

    print(
        "Warning: irrigation scaler could not be loaded:",
        exc
    )


# =========================================================
# CROP WATER FACTOR
# =========================================================

CROP_WATER_FACTOR = {

    "rice": 1.00,
    "maize": 0.75,
    "chickpea": 0.45,
    "cotton": 0.70,
    "wheat": 0.65,
    "groundnut": 0.60,
    "banana": 0.90,

    # Additional crops
    "sugarcane": 1.20,
    "tomato": 0.80,
    "potato": 0.70,
    "onion": 0.60,
    "millet": 0.50,
    "soybean": 0.70,
    "sorghum": 0.55,
    "barley": 0.55

}


# =========================================================
# CROP NORMALIZATION
# =========================================================

def normalize_crop(crop_type):

    if not crop_type:

        raise ValueError(
            "Crop type is required."
        )

    crop = (
        str(crop_type)
        .strip()
        .lower()
    )

    if crop not in CROP_WATER_FACTOR:

        raise ValueError(
            f"Unsupported crop type: {crop_type}"
        )

    return crop


# =========================================================
# PREPROCESS IRRIGATION
# =========================================================

def preprocess_irrigation(data):

    crop = normalize_crop(
        data.crop_type
    )

    crop_water_factor = (
        CROP_WATER_FACTOR[crop]
    )

    features = {

        "soil_moisture":
            float(data.soil_moisture),

        "humidity":
            float(data.humidity),

        "temperature":
            float(data.temperature),

        "rainfall":
            float(data.rainfall),

        "soil_temperature":
            float(data.soil_temperature),

        "wind_speed":
            float(data.wind_speed),

        "rain_forecast":
            float(data.rain_forecast),

        "nitrogen":
            float(data.nitrogen),

        "phosphorus":
            float(data.phosphorus),

        "potassium":
            float(data.potassium),

        "ph":
            float(data.ph),

        "crop_water_factor":
            float(crop_water_factor)

    }

    return pd.DataFrame(
        [features]
    )


# =========================================================
# CROP-SPECIFIC MOISTURE LIMITS
# =========================================================

CROP_MOISTURE_LIMITS = {

    "rice": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "maize": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "chickpea": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "cotton": {
        "critical": 23,
        "low": 32,
        "good": 52
    },

    "wheat": {
        "critical": 23,
        "low": 32,
        "good": 52
    },

    "groundnut": {
        "critical": 22,
        "low": 32,
        "good": 52
    },

    "banana": {
        "critical": 30,
        "low": 40,
        "good": 60
    },

    "sugarcane": {
        "critical": 30,
        "low": 42,
        "good": 65
    },

    "tomato": {
        "critical": 25,
        "low": 35,
        "good": 55
    },

    "potato": {
        "critical": 23,
        "low": 33,
        "good": 55
    },

    "onion": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "millet": {
        "critical": 18,
        "low": 28,
        "good": 48
    },

    "soybean": {
        "critical": 23,
        "low": 33,
        "good": 55
    },

    "sorghum": {
        "critical": 20,
        "low": 30,
        "good": 50
    },

    "barley": {
        "critical": 20,
        "low": 30,
        "good": 50
    }

}


# =========================================================
# IRRIGATION DECISION
# =========================================================

def calculate_irrigation_decision(

    crop,
    soil_moisture,
    humidity,
    temperature,
    rainfall,
    rain_forecast,
    wind_speed

):

    limits = (
        CROP_MOISTURE_LIMITS.get(

            crop,

            {
                "critical": 25,
                "low": 35,
                "good": 55
            }

        )
    )

    critical = limits["critical"]
    low = limits["low"]
    good = limits["good"]


    # =====================================================
    # HEAVY RAINFALL PROTECTION
    # =====================================================

    if rainfall >= 5:

        if soil_moisture <= critical:

            return (

                "Irrigate soon",

                "Soil moisture is very low despite recent rainfall. "
                "Monitor the field closely and provide water if moisture "
                "does not recover."

            )

        return (

            "No irrigation",

            "Recent rainfall has reduced the need for irrigation."

        )


    # =====================================================
    # STRONG RAIN FORECAST
    # =====================================================

    if rain_forecast >= 70:

        if soil_moisture <= critical:

            return (

                "Monitor",

                "Soil moisture is low, but significant rainfall is "
                "forecast. Recheck the field before irrigating."

            )

        return (

            "No irrigation",

            "Rain is expected soon, so irrigation can be avoided."

        )


    # =====================================================
    # CRITICAL MOISTURE
    # =====================================================

    if soil_moisture <= critical:

        return (

            "Irrigate now",

            "Soil moisture is critically low."

        )


    # =====================================================
    # LOW MOISTURE
    # =====================================================

    if soil_moisture <= low:

        if (

            temperature >= 32
            and humidity <= 45
            and rain_forecast < 40

        ):

            return (

                "Irrigate now",

                "Soil moisture is low and hot, dry weather is "
                "increasing the crop's water requirement."

            )

        return (

            "Irrigate soon",

            "Soil moisture is below the recommended range "
            "for this crop."

        )


    # =====================================================
    # MODERATE MOISTURE + HOT WEATHER
    # =====================================================

    if (

        soil_moisture < good
        and temperature >= 35
        and humidity < 40
        and rain_forecast < 30

    ):

        return (

            "Irrigate soon",

            "The soil still contains moisture, but hot and dry "
            "conditions are increasing water demand."

        )


    # =====================================================
    # HIGH WIND + MODERATE MOISTURE
    # =====================================================

    if (

        soil_moisture < good
        and wind_speed >= 25
        and humidity < 50
        and rain_forecast < 30

    ):

        return (

            "Irrigate soon",

            "Dry and windy conditions may increase water loss "
            "from the soil."

        )


    # =====================================================
    # SUFFICIENT MOISTURE
    # =====================================================

    if soil_moisture >= good:

        return (

            "No irrigation",

            "Soil moisture is sufficient for the crop."

        )


    # =====================================================
    # DEFAULT
    # =====================================================

    return (

        "Monitor",

        "Soil moisture is currently acceptable. Continue "
        "monitoring the field conditions."

    )


# =========================================================
# IRRIGATION PREDICTION
# =========================================================

def predict_irrigation(features):

    if features is None:

        raise ValueError(
            "Irrigation features are missing."
        )


    if features.empty:

        raise ValueError(
            "Irrigation feature data is empty."
        )


    # =====================================================
    # READ VALUES
    # =====================================================

    soil_moisture = float(
        features["soil_moisture"].iloc[0]
    )

    humidity = float(
        features["humidity"].iloc[0]
    )

    temperature = float(
        features["temperature"].iloc[0]
    )

    rainfall = float(
        features["rainfall"].iloc[0]
    )

    rain_forecast = float(
        features["rain_forecast"].iloc[0]
    )

    wind_speed = float(
        features["wind_speed"].iloc[0]
    )

    crop_water_factor = float(
        features["crop_water_factor"].iloc[0]
    )


    # =====================================================
    # IDENTIFY CROP
    # =====================================================

    crop = None

    for name, factor in CROP_WATER_FACTOR.items():

        if abs(
            factor - crop_water_factor
        ) < 0.0001:

            crop = name

            break


    if crop is None:

        crop = "rice"


    # =====================================================
    # FINAL AGRICULTURAL DECISION
    # =====================================================

    status, reason = calculate_irrigation_decision(

        crop=crop,

        soil_moisture=soil_moisture,

        humidity=humidity,

        temperature=temperature,

        rainfall=rainfall,

        rain_forecast=rain_forecast,

        wind_speed=wind_speed

    )


    # =====================================================
    # ML PREDICTION
    # =====================================================

    ml_prediction = None

    prediction_probabilities = {}


    try:

        if model is not None:

            model_columns = [

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
                "crop_water_factor"

            ]


            # ---------------------------------------------
            # KEEP DATAFRAME FEATURE NAMES
            # ---------------------------------------------

            model_features = (
                features[
                    model_columns
                ]
                .copy()
                .astype(float)
            )


            # ---------------------------------------------
            # SCALE
            # ---------------------------------------------

            if scaler is not None:

                values = scaler.transform(
                    model_features
                )

            else:

                values = model_features


            # ---------------------------------------------
            # RANDOM FOREST PREDICTION
            # ---------------------------------------------

            prediction = model.predict(
                values
            )


            if len(prediction) > 0:

                ml_prediction = str(
                    prediction[0]
                )


            print(
                "ML irrigation prediction:",
                ml_prediction
            )


            # ---------------------------------------------
            # PREDICTION PROBABILITIES
            # ---------------------------------------------

            if hasattr(
                model,
                "predict_proba"
            ):

                probabilities = (
                    model.predict_proba(
                        values
                    )
                )


                classes = model.classes_


                if (
                    len(probabilities) > 0
                ):

                    prediction_probabilities = {

                        str(label):
                            round(
                                float(probability),
                                4
                            )

                        for label, probability
                        in zip(

                            classes,

                            probabilities[0]

                        )

                    }


                    print(
                        "Prediction probabilities:",
                        prediction_probabilities
                    )


    except Exception as exc:

        print(
            "ML prediction skipped:",
            exc
        )


    # =====================================================
    # IRRIGATION SCORE
    # =====================================================

    # Score represents water stress.
    #
    # Higher score = greater irrigation requirement.
    #
    # This score is intentionally based on the agricultural
    # decision inputs rather than replacing the dataset model.

    limits = (
        CROP_MOISTURE_LIMITS.get(
            crop,
            {
                "critical": 25,
                "low": 35,
                "good": 55
            }
        )
    )

    critical = float(
        limits["critical"]
    )

    good = float(
        limits["good"]
    )


    moisture_stress = max(

        0.0,

        good - soil_moisture

    )


    temperature_stress = max(

        0.0,

        temperature - 25.0

    ) * 0.50


    humidity_stress = max(

        0.0,

        50.0 - humidity

    ) * 0.15


    wind_stress = max(

        0.0,

        wind_speed - 20.0

    ) * 0.10


    rainfall_relief = min(

        rainfall * 1.5,

        15.0

    )


    forecast_relief = (

        rain_forecast
        / 10.0

    )


    irrigation_score = (

        moisture_stress
        + temperature_stress
        + humidity_stress
        + wind_stress
        - rainfall_relief
        - forecast_relief

    )


    # Critical moisture should always produce
    # a strong irrigation score.

    if soil_moisture <= critical:

        irrigation_score = max(

            irrigation_score,

            75.0

        )


    irrigation_score = max(

        0.0,

        min(

            100.0,

            float(irrigation_score)

        )

    )


    # =====================================================
    # WATER NEED
    # =====================================================

    if status == "Irrigate now":

        water_need = "HIGH"

    elif status == "Irrigate soon":

        water_need = "MEDIUM"

    elif status == "Monitor":

        water_need = "LOW"

    else:

        water_need = "NONE"


    # =====================================================
    # NOTIFICATION REQUIRED
    # =====================================================

    notification_required = (

        status in [

            "Irrigate now",

            "Irrigate soon"

        ]

    )


    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {

        "irrigation_status":
            status,

        "water_need":
            water_need,

        "reason":
            reason,

        "crop_type":
            crop,

        "soil_moisture":
            round(
                soil_moisture,
                2
            ),

        "temperature":
            round(
                temperature,
                2
            ),

        "humidity":
            round(
                humidity,
                2
            ),

        "rainfall":
            round(
                rainfall,
                2
            ),

        "rain_forecast":
            round(
                rain_forecast,
                2
            ),

        "irrigation_score":
            round(
                irrigation_score,
                3
            ),

        "ml_prediction":
            ml_prediction,

        "prediction_probabilities":
            prediction_probabilities,

        "notification_required":
            notification_required,

        "model":
            "Random Forest + Irrigation Dataset + Weather + Soil Moisture",

        "features_used":
            12

    }