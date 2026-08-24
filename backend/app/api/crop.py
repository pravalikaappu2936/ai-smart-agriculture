from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.models.user import User

from app.schemas.crop_schema import CropInput

from app.ml_models.crop_preprocessing import (
    preprocess_crop
)

from app.ml_models.crop_model import (
    predict_crop
)

from app.ml_models.crop_recommendation import (
    get_crop_advice
)


router = APIRouter(
    prefix="/crop",
    tags=["Crop Recommendation"]
)


# =========================================================
# STATUS
# =========================================================

@router.get("/")
def crop_status(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "message":
            "Crop Recommendation Module Ready",

        "user":
            current_user.username,

        "model":
            "Random Forest",

        "dataset":
            "2200 crop records"
    }


# =========================================================
# PREDICTION FUNCTION
# =========================================================

def process_crop_prediction(
    crop: CropInput
):

    # -----------------------------------------------------
    # Preprocess
    # -----------------------------------------------------

    processed_data = (
        preprocess_crop(crop)
    )

    # -----------------------------------------------------
    # Predict
    # -----------------------------------------------------

    result = predict_crop(
        processed_data
    )

    # -----------------------------------------------------
    # Advice
    # -----------------------------------------------------

    advice = get_crop_advice(
        result["recommended_crop"]
    )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {
        "recommended_crop":
            result["recommended_crop"],

        "confidence":
            result["confidence"],

        "advice":
            advice,

        "model":
            result["model"],

        "dataset_records":
            result["dataset_records"],

        "crop_classes":
            result["crop_classes"],

        "model_accuracy":
            result["accuracy"]
    }


# =========================================================
# /predict
# =========================================================

@router.post("/predict")
def predict_crop_api(
    crop: CropInput,

    current_user: User = Depends(
        get_current_user
    )
):

    result = process_crop_prediction(
        crop
    )

    result["user"] = (
        current_user.username
    )

    return result


# =========================================================
# /recommend
# =========================================================
#
# Kept for your existing Crop.jsx
#
# =========================================================

@router.post("/recommend")
def recommend_crop_api(
    crop: CropInput,

    current_user: User = Depends(
        get_current_user
    )
):

    result = process_crop_prediction(
        crop
    )

    result["user"] = (
        current_user.username
    )

    return result