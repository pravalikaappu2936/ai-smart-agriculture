from fastapi import APIRouter, HTTPException

from app.services.weather_service import (
    get_weather_for_location,
    get_weather_by_coordinates,
    search_locations,
)


router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


# =========================================================
# LOCATION SEARCH
# =========================================================

@router.get("/search")
def search_weather_location(
    village: str,
    district: str = "",
    state: str = "",
):

    village = village.strip()
    district = district.strip()
    state = state.strip()


    if not village:

        raise HTTPException(
            status_code=400,
            detail="Village, town or city is required.",
        )


    try:

        results = search_locations(
            village=village,
            district=district,
            state=state,
        )


        return {
            "results": results
        }


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# WEATHER BY LOCATION
# =========================================================

@router.post("/current")
def current_weather(
    payload: dict
):

    location = payload.get(
        "location"
    )


    if not location:

        raise HTTPException(
            status_code=400,
            detail="Location is required.",
        )


    try:

        return get_weather_for_location(
            location
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# WEATHER BY COORDINATES
# =========================================================

@router.post(
    "/current-by-coordinates"
)
def current_weather_by_coordinates(
    payload: dict
):

    latitude = payload.get(
        "latitude"
    )

    longitude = payload.get(
        "longitude"
    )


    if (
        latitude is None
        or longitude is None
    ):

        raise HTTPException(
            status_code=400,
            detail="Latitude and longitude are required.",
        )


    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )


    except (
        TypeError,
        ValueError
    ):

        raise HTTPException(
            status_code=400,
            detail="Latitude and longitude must be numbers.",
        )


    if not -90 <= latitude <= 90:

        raise HTTPException(
            status_code=400,
            detail="Invalid latitude.",
        )


    if not -180 <= longitude <= 180:

        raise HTTPException(
            status_code=400,
            detail="Invalid longitude.",
        )


    try:

        return get_weather_by_coordinates(
            latitude,
            longitude
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


# =========================================================
# ROOT
# =========================================================

@router.get("/")
def weather_home():

    return {

        "message":
            "Weather API is working",

        "endpoints": [

            "/weather/search",

            "/weather/current",

            "/weather/current-by-coordinates"
        ]
    }