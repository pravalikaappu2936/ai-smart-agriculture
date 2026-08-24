from fastapi import APIRouter

from app.schemas.iot_schema import (
    IoTSensorData
)


router = APIRouter(
    prefix="/iot",
    tags=["IoT Sensors"]
)


# =========================================================
# TEMPORARY SENSOR DATA
# =========================================================

latest_sensor_data = {

    "soil_moisture": 42.5,

    "temperature": 28.4,

    "humidity": 65.0,

    "rainfall": 12.0,

    "nitrogen": 80.0,

    "phosphorus": 45.0,

    "potassium": 50.0,

    "ph": 6.5
}


# =========================================================
# SENSOR STATUS
# =========================================================

@router.get(
    "/status"
)
def iot_status():

    return {

        "message":
            "IoT Sensor Module Ready",

        "status":
            "connected"
    }


# =========================================================
# GET LATEST SENSOR DATA
# =========================================================

@router.get(
    "/latest"
)
def get_latest_sensor_data():

    return {

        "status":
            "success",

        "data":
            latest_sensor_data
    }


# =========================================================
# UPDATE SENSOR DATA
# =========================================================

@router.post(
    "/update"
)
def update_sensor_data(
    data: IoTSensorData
):

    global latest_sensor_data

    latest_sensor_data = (
        data.model_dump()
    )

    return {

        "status":
            "success",

        "message":
            "Sensor data updated successfully",

        "data":
            latest_sensor_data
    }