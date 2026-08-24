from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.auth import (
    get_current_user
)

from app.models.user import User

from app.models.notification import (
    Notification
)

from app.schemas.irrigation_schema import (
    IrrigationInput,
    IrrigationResponse
)

from app.ml_models.irrigation_preprocessing import (
    preprocess_irrigation
)

from app.ml_models.irrigation_model import (
    predict_irrigation
)

from app.services.weather_service import (
    get_weather_for_location
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/irrigation",
    tags=["Irrigation"]
)


# =========================================================
# AGRICULTURAL ADVICE
# =========================================================

ADVICE_MAP = {

    "No irrigation":
        "The crop has sufficient soil moisture. Irrigation is not required now.",

    "Monitor":
        "Continue monitoring soil moisture and weather conditions.",

    "Irrigate soon":
        "Soil moisture is becoming low for this crop. Irrigation may be required soon. Monitor the field closely.",

    "Irrigate now":
        "Soil moisture is low for this crop and irrigation is recommended now."
}


# =========================================================
# WEATHER VALUES
# =========================================================

def get_weather_values(weather_data):

    if not isinstance(
        weather_data,
        dict
    ):

        raise ValueError(
            "Invalid weather response."
        )


    current = weather_data.get(
        "current",
        {}
    )


    forecast = weather_data.get(
        "forecast",
        {}
    )


    if not isinstance(
        current,
        dict
    ):

        current = {}


    if not isinstance(
        forecast,
        dict
    ):

        forecast = {}


    # =====================================================
    # TEMPERATURE
    # =====================================================

    temperature = current.get(
        "temperature_2m"
    )


    if temperature is None:

        temperature = current.get(
            "temperature"
        )


    # =====================================================
    # HUMIDITY
    # =====================================================

    humidity = current.get(
        "relative_humidity_2m"
    )


    if humidity is None:

        humidity = current.get(
            "humidity"
        )


    # =====================================================
    # RAINFALL
    # =====================================================

    rainfall = current.get(
        "rain"
    )


    if rainfall is None:

        rainfall = current.get(
            "precipitation",
            0
        )


    # =====================================================
    # RAIN PROBABILITY
    # =====================================================

    rain_probability = 0.0


    probability_values = forecast.get(
        "precipitation_probability_max",
        []
    )


    if isinstance(
        probability_values,
        list
    ) and probability_values:

        try:

            rain_probability = float(
                probability_values[0]
            )

        except (
            TypeError,
            ValueError
        ):

            rain_probability = 0.0


    elif isinstance(
        probability_values,
        (int, float)
    ):

        try:

            rain_probability = float(
                probability_values
            )

        except (
            TypeError,
            ValueError
        ):

            rain_probability = 0.0


    return {

        "temperature":
            float(temperature)
            if temperature is not None
            else None,

        "humidity":
            float(humidity)
            if humidity is not None
            else None,

        "rainfall":
            float(rainfall)
            if rainfall is not None
            else 0.0,

        "rain_probability":
            rain_probability
    }


# =========================================================
# CREATE IRRIGATION NOTIFICATION
# =========================================================

def create_irrigation_notification(

    db: Session,

    current_user: User,

    data: IrrigationInput,

    result: dict

):

    status = result.get(
        "irrigation_status"
    )


    # =====================================================
    # NOT REQUIRED
    # =====================================================

    if status not in [

        "Irrigate now",

        "Irrigate soon"

    ]:

        return False


    # =====================================================
    # CHECK EXISTING UNREAD IRRIGATION NOTIFICATION
    # =====================================================

    existing_notifications = (

        db.query(
            Notification
        )

        .filter(

            Notification.user_id
            == current_user.id,

            Notification.is_read
            == False

        )

        .order_by(

            Notification.created_at.desc()

        )

        .all()

    )


    for existing in existing_notifications:

        existing_title = str(

            getattr(

                existing,

                "title",

                ""

            )

        ).lower()


        if "irrigation" in existing_title:

            return False


    # =====================================================
    # IRRIGATE NOW
    # =====================================================

    if status == "Irrigate now":

        title = (
            "💧 Irrigation Alert"
        )


        message = (

            f"Your {data.crop_type} field "
            f"at {data.location} needs irrigation now. "

            f"Soil moisture is "
            f"{data.soil_moisture:.1f}%. "

            f"{result.get('reason', '')} "

            f"Please irrigate the field."

        )


    # =====================================================
    # IRRIGATE SOON
    # =====================================================

    else:

        title = (
            "💧 Irrigation Reminder"
        )


        message = (

            f"Your {data.crop_type} field "
            f"at {data.location} may need irrigation soon. "

            f"Current soil moisture is "
            f"{data.soil_moisture:.1f}%. "

            f"{result.get('reason', '')} "

            f"Please monitor the field."

        )


    # =====================================================
    # CREATE
    # =====================================================

    notification = Notification(

        user_id=current_user.id,

        title=title,

        message=message,

        is_read=False

    )


    db.add(
        notification
    )


    db.commit()


    db.refresh(
        notification
    )


    print(
        "Irrigation notification created:",
        notification.id
    )


    return True


# =========================================================
# IRRIGATION PREDICTION
# =========================================================

@router.post(
    "/predict",
    response_model=IrrigationResponse
)
def irrigation_prediction(

    data: IrrigationInput,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    try:

        # =================================================
        # WEATHER
        # =================================================

        weather_data = (
            get_weather_for_location(
                data.location
            )
        )


        weather = (
            get_weather_values(
                weather_data
            )
        )


        # =================================================
        # WEATHER VALUES
        # =================================================

        weather_temperature = (
            weather["temperature"]
        )


        weather_humidity = (
            weather["humidity"]
        )


        weather_rainfall = (
            weather["rainfall"]
        )


        rain_probability = (
            weather["rain_probability"]
        )


        # =================================================
        # COMBINE IOT + WEATHER
        # =================================================

        if weather_temperature is not None:

            data.temperature = (
                weather_temperature
            )


        if weather_humidity is not None:

            data.humidity = (
                weather_humidity
            )


        data.rainfall = (
            weather_rainfall
        )


        data.rain_forecast = (
            rain_probability
        )


        # =================================================
        # PREPROCESS
        # =================================================

        features = (
            preprocess_irrigation(
                data
            )
        )


        print(
            "========================================"
        )

        print(
            "IRRIGATION FEATURES:"
        )

        print(
            features.to_dict(
                orient="records"
            )
        )

        print(
            "========================================"
        )


        # =================================================
        # PREDICTION
        # =================================================

        result = (
            predict_irrigation(
                features
            )
        )


        if not isinstance(
            result,
            dict
        ):

            raise ValueError(
                "Invalid irrigation model response."
            )


        status = result.get(
            "irrigation_status"
        )


        if not status:

            raise ValueError(
                "Irrigation model did not return a status."
            )


        # =================================================
        # ADVICE
        # =================================================

        advice = ADVICE_MAP.get(

            status,

            "Continue monitoring soil moisture and weather conditions."

        )


        # =================================================
        # NOTIFICATION
        # =================================================

        notification_created = (
            create_irrigation_notification(

                db=db,

                current_user=current_user,

                data=data,

                result=result

            )
        )


        # =================================================
        # SCORE
        # =================================================

        try:

            irrigation_score = float(

                result.get(

                    "irrigation_score",

                    0.0

                )

            )

        except (
            TypeError,
            ValueError
        ):

            irrigation_score = 0.0


        # =================================================
        # FEATURES USED
        # =================================================

        try:

            features_used = int(

                result.get(

                    "features_used",

                    12

                )

            )

        except (
            TypeError,
            ValueError
        ):

            features_used = 12


        # =================================================
        # FINAL RESPONSE
        # =================================================

        response = {

            # ---------------------------------------------
            # DECISION
            # ---------------------------------------------

            "irrigation_status":
                status,

            "water_need":
                result.get(
                    "water_need",
                    "NONE"
                ),

            "reason":
                result.get(
                    "reason",
                    advice
                ),


            # ---------------------------------------------
            # SCORE
            # ---------------------------------------------

            "irrigation_score":
                irrigation_score,

            "ml_prediction":
                result.get(
                    "ml_prediction"
                ),


            # ---------------------------------------------
            # MODEL
            # ---------------------------------------------

            "model":
                result.get(
                    "model",
                    "Crop + Soil Moisture + Weather + ML"
                ),

            "features_used":
                features_used,


            # ---------------------------------------------
            # CROP
            # ---------------------------------------------

            "crop_type":
                data.crop_type,

            "location":
                data.location,


            # ---------------------------------------------
            # SOIL
            # ---------------------------------------------

            "soil_moisture":
                float(
                    data.soil_moisture
                ),


            # ---------------------------------------------
            # WEATHER
            # ---------------------------------------------

            "weather_temperature":
                weather_temperature,

            "weather_humidity":
                weather_humidity,

            "rainfall":
                weather_rainfall,

            "rain_probability":
                rain_probability,


            # ---------------------------------------------
            # NOTIFICATION
            # ---------------------------------------------

            "notification_required":
                result.get(
                    "notification_required",
                    False
                ),

            "notification_created":
                notification_created,


            # ---------------------------------------------
            # ADVICE
            # ---------------------------------------------

            "advice":
                advice

        }


        print(
            "FINAL IRRIGATION RESPONSE:"
        )

        print(
            response
        )

        print(
            "========================================"
        )


        return response


    # =====================================================
    # VALUE ERROR
    # =====================================================

    except ValueError as exc:

        print(
            "Irrigation ValueError:",
            exc
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc)

        )


    # =====================================================
    # FILE ERROR
    # =====================================================

    except FileNotFoundError as exc:

        print(
            "Irrigation FileNotFoundError:",
            exc
        )


        raise HTTPException(

            status_code=500,

            detail=str(exc)

        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as exc:

        print(
            "Irrigation prediction error:",
            exc
        )


        raise HTTPException(

            status_code=500,

            detail=str(exc)

        )