from app.ml_models.crop_preprocessing import preprocess_crop
from app.ml_models.crop_model import predict_crop
from app.ml_models.crop_recommendation import get_crop_advice


def recommend_crop(data):

    processed_data = preprocess_crop(
        data
    )

    result = predict_crop(
        processed_data
    )

    crop = result[
        "recommended_crop"
    ]

    return {
        "crop": crop,

        "confidence":
            result["confidence"],

        "advice":
            get_crop_advice(crop),

        "model":
            result["model"],

        "dataset_records":
            result["dataset_records"],

        "crop_classes":
            result["crop_classes"],

        "model_accuracy":
            result["accuracy"]
    }