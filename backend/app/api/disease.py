from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.ml_models.disease_model import predict_disease
from app.schemas.disease_schema import DiseasePredictionResponse


router = APIRouter(
    prefix="/disease",
    tags=["Plant Disease Detection"],
)


MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/predict",
    response_model=DiseasePredictionResponse,
)
async def predict_plant_disease(
    file: UploadFile = File(...),
):
    # Check that the uploaded file is an image
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file.",
        )

    # Read uploaded image
    contents = await file.read()

    # Check file size
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must be less than 5 MB.",
        )

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    # Convert uploaded file to PIL image
    try:
        image = Image.open(BytesIO(contents))
        image = image.convert("RGB")

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    # Run disease prediction
    try:
        result = predict_disease(image)
        return result

    except Exception as error:
        print("PLANT DISEASE PREDICTION ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Plant disease prediction failed.",
        ) from error