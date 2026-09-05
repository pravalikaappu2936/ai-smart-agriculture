from pydantic import BaseModel, Field


class CropYieldInput(BaseModel):

    year: int = Field(
        ...,
        ge=2000,
        le=2100,
    )

    state: str = Field(
        ...,
        min_length=2,
        max_length=80,
    )

    crop: str = Field(
        ...,
        min_length=2,
        max_length=80,
    )

    season: str = Field(
        ...,
        min_length=2,
        max_length=40,
    )

    area: float = Field(
        ...,
        gt=0,
    )

    annual_rainfall: float = Field(
        ...,
        ge=0,
    )

    fertilizer: float = Field(
        ...,
        ge=0,
    )

    pesticide: float = Field(
        ...,
        ge=0,
    )