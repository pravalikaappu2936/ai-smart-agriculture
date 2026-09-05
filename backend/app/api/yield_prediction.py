from fastapi import APIRouter, HTTPException

from app.schemas.yield_schema import CropYieldInput
from app.ml_models.yield_model import predict_yield


router = APIRouter(
    prefix="/yield",
    tags=["Crop Yield Prediction"],
)


@router.post("/predict")
def predict_crop_yield(
    data: CropYieldInput,
):

    try:

        result = predict_yield(
            data.model_dump()
        )

        return {
            "success": True,
            **result,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    except Exception as error:

        print(
            "CROP YIELD PREDICTION ERROR:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Crop yield prediction failed.",
        )