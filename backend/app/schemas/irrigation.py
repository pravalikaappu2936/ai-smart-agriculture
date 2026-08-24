from pydantic import BaseModel


class IrrigationRequest(BaseModel):
    temperature: float
    humidity: float
    soil_moisture: float
    rainfall: float


class IrrigationResponse(BaseModel):
    water_required: float
    confidence: float