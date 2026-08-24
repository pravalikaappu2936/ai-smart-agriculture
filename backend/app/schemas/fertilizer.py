from pydantic import BaseModel


class FertilizerRequest(BaseModel):
    crop_name: str
    soil_type: str
    nitrogen: float
    phosphorus: float
    potassium: float


class FertilizerResponse(BaseModel):
    recommended_fertilizer: str
    confidence: float