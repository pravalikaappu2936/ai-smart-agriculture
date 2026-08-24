from pydantic import BaseModel, Field


# ============================================================
# MANUAL WEATHER LOCATION
# ============================================================

class WeatherLocationInput(BaseModel):

    location: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Indian city, district, village, or location"
    )


# ============================================================
# COORDINATE WEATHER LOCATION
# ============================================================

class WeatherCoordinateInput(BaseModel):

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude"
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude"
    )