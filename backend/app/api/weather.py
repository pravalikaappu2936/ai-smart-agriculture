from fastapi import APIRouter, HTTPException

from app.services.weather_service import (
    get_weather_for_location,
    get_weather_by_coordinates,
    search_locations,
)


# =========================================================
# ROUTER
# =========================================================

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
    """
    Search for a village, town or city.

    Example:

        /weather/search?village=Chitradurga&state=Karnataka
    """

    village = village.strip()
    district = district.strip()
    state = state.strip()

    # -----------------------------------------------------
    # VALIDATE VILLAGE
    # -----------------------------------------------------

    if not village:

        raise HTTPException(
            status_code=400,
            detail="Village, town or city is required.",
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    try:

        results = search_locations(
            village=village,
            district=district,
            state=state,
        )

        return {
            "results": results
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )


# =========================================================
# WEATHER BY LOCATION
# =========================================================

@router.post("/current")
def current_weather(
    payload: dict
):
    """
    Get current weather and 7-day forecast
    using a location name.
    """

    # -----------------------------------------------------
    # GET LOCATION
    # -----------------------------------------------------

    location = payload.get(
        "location"
    )

    if not location:

        raise HTTPException(
            status_code=400,
            detail="Location is required.",
        )

    location = str(
        location
    ).strip()

    if not location:

        raise HTTPException(
            status_code=400,
            detail="Location is required.",
        )

    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------

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

        # -------------------------------------------------
        # WEATHER SERVICE / RATE LIMIT
        # -------------------------------------------------

        raise HTTPException(
            status_code=503,
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
    """
    Get current weather and 7-day forecast
    directly using latitude and longitude.

    Example body:

    {
        "latitude": 14.238,
        "longitude": 76.3933
    }
    """

    # =====================================================
    # GET LATITUDE
    # =====================================================

    latitude = payload.get(
        "latitude"
    )

    # =====================================================
    # GET LONGITUDE
    # =====================================================

    longitude = payload.get(
        "longitude"
    )

    # =====================================================
    # REQUIRED CHECK
    # =====================================================

    if (
        latitude is None
        or longitude is None
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Latitude and longitude "
                "are required."
            ),
        )

    # =====================================================
    # CONVERT TO FLOAT
    # =====================================================

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
            detail=(
                "Latitude and longitude "
                "must be numbers."
            ),
        )

    # =====================================================
    # VALIDATE LATITUDE
    # =====================================================

    if not -90 <= latitude <= 90:

        raise HTTPException(
            status_code=400,
            detail=(
                "Latitude must be between "
                "-90 and 90."
            ),
        )

    # =====================================================
    # VALIDATE LONGITUDE
    # =====================================================

    if not -180 <= longitude <= 180:

        raise HTTPException(
            status_code=400,
            detail=(
                "Longitude must be between "
                "-180 and 180."
            ),
        )

    # =====================================================
    # GET WEATHER
    # =====================================================

    try:

        weather_data = (
            get_weather_by_coordinates(
                latitude,
                longitude
            )
        )

        return weather_data

    # =====================================================
    # INVALID INPUT
    # =====================================================

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # =====================================================
    # WEATHER SERVICE ERROR
    # =====================================================

    except Exception as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
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

            "/weather/current-by-coordinates",

        ],
    }