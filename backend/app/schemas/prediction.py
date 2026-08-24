from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    id: int
    module: str
    prediction: str
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)