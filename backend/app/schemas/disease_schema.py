from typing import Optional

from pydantic import BaseModel, Field


class DiseasePredictionResponse(BaseModel):
    success: bool = True
    crop: str
    disease: str
    confidence: float = Field(ge=0, le=100)
    class_index: int = Field(ge=0)
    treatment: str
    prevention: str
    model: str
    model_accuracy: Optional[float] = None
    dataset_images_used: Optional[int] = None
    total_classes: int = Field(ge=1)