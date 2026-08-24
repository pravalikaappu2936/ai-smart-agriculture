import requests

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class WeatherRequest(BaseModel):

    # Manual location
    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    # Map-selected coordinates
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )


# ============================================================
# CITY ALIASES
# ============================================================

CITY_ALIASES = {

    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",

    "bombay": "Mumbai",
    "mumbai": "Mumbai",

    "calcutta": "Kolkata",
    "kolkata": "Kolkata",

    "madras": "Chennai",
    "chennai": "Chennai",

    "delhi": "New Delhi",
    "new delhi": "New Delhi",

    "mysore": "Mysuru",
    "mysuru": "Mysuru",

    "mangalore": "Mangaluru",
    "mangaluru": "Mangaluru",

    "cochin": "Kochi",
    "kochi": "Kochi",

    "vizag": "Visakhapatnam",
    "visakhapatnam": "Visakhapatnam"
}


# ============================================================
# NORMALIZE CITY
# ============================================================

def normalize_city(location: str) -> str:

    location = location.strip()

    if not location:

        raise HTTPException(
            status_code=400,
            detail="Location cannot be empty."
        )

    return CITY_ALIASES.get(
        location.lower(),
        location
    )


# ============================================================
# GEOCODING - MANUAL LOCATION
# ============================================================

def get_coordinates(location: str):

    search_location = normalize_city(location)

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    params = {
        "name": search_location,
        "count": 10,
        "language": "en",
        "format": "json",
        "countryCode": "IN"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Location service unavailable: {str(e)}"
            )
        )

    results = data.get("results", [])

    if not results:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Location '{location}' "
                "was not found in India."
            )
        )

    result = next(
        (
            item
            for item in results
            if item.get(
                "country_code",
                ""
            ).upper() == "IN"
        ),
        results[0]
    )

    return {
        "name": result.get("name"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "country": result.get("country"),
        "country_code": result.get("country_code"),
        "state": result.get("admin1"),
        "timezone": result.get("timezone")
    }


# ============================================================
# MAP LOCATION
# ============================================================

def get_coordinates_from_map(
    latitude: float,
    longitude: float
):

    """
    Coordinates selected directly by the farmer
    from the map.

    No city search is performed.
    """

    return {
        "name": "Selected Map Location",
        "latitude": latitude,
        "longitude": longitude,
        "country": "India",
        "country_code": "IN",
        "state": None,
        "timezone": None
    }


# ============================================================
# RESOLVE LOCATION
# ============================================================

def resolve_location(request: WeatherRequest):

    # --------------------------------------------------------
    # OPTION 1: MAP
    # --------------------------------------------------------

    if (
        request.latitude is not None
        and request.longitude is not None
    ):

        return get_coordinates_from_map(
            request.latitude,
            request.longitude
        )


    # --------------------------------------------------------
    # OPTION 2: MANUAL LOCATION
    # --------------------------------------------------------

    if request.location is not None:

        location = request.location.strip()

        if not location:

            raise HTTPException(
                status_code=400,
                detail="Location is required."
            )

        return get_coordinates(location)


    # --------------------------------------------------------
    # NOTHING PROVIDED
    # --------------------------------------------------------

    raise HTTPException(
        status_code=400,
        detail=(
            "Please provide either a location "
            "or latitude and longitude."
        )
    )


# ============================================================
# GET WEATHER DATA
# ============================================================

def get_weather_data(
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None
):

    # Resolve coordinates

    if (
        latitude is not None
        and longitude is not None
    ):

        coordinates = get_coordinates_from_map(
            latitude,
            longitude
        )

    elif location is not None:

        coordinates = get_coordinates(
            location
        )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide either a location "
                "or latitude and longitude."
            )
        )


    latitude = coordinates["latitude"]
    longitude = coordinates["longitude"]


    # ========================================================
    # OPEN-METEO WEATHER API
    # ========================================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )


    weather_params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m"
        ]),

        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max"
        ]),

        "forecast_days": 7,

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }


    try:

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=15
        )

        response.raise_for_status()

        weather_data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Weather service unavailable: {str(e)}"
            )
        )


    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "status": "success",

        "location": coordinates,

        "current": weather_data.get(
            "current",
            {}
        ),

        "forecast": weather_data.get(
            "daily",
            {}
        )
    }


# ============================================================
# CURRENT WEATHER
# ============================================================

@router.post("/current")
def current_weather(
    request: WeatherRequest,
    current_user=Depends(get_current_user)
):

    weather_data = get_weather_data(
        location=request.location,
        latitude=request.latitude,
        longitude=request.longitude
    )

    return {

        "status": "success",

        "location": weather_data["location"],

        "current": weather_data["current"]
    }


# ============================================================
# 7-DAY FORECAST
# ============================================================

@router.post("/forecast")
def weather_forecast(
    request: WeatherRequest,
    current_user=Depends(get_current_user)
):

    weather_data = get_weather_data(
        location=request.location,
        latitude=request.latitude,
        longitude=request.longitude
    )

    return {

        "status": "success",

        "location": weather_data["location"],

        "forecast": weather_data["forecast"]
    }


# ============================================================
# WEATHER STATUS
# ============================================================

@router.get("/")
def weather_status(
    current_user=Depends(get_current_user)
):

    return {

        "status": "success",

        "message": "Weather Module Ready"
    }