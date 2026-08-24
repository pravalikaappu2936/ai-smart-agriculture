from fastapi import APIRouter, HTTPException

from app.schemas.fertilizer_schema import FertilizerInput

from app.ml_models.fertilizer_model import (
    predict_fertilizer
)

from app.services.dataset_service import (
    load_fertilizer_data
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/fertilizer",
    tags=["Fertilizer"]
)


# =========================================================
# FERTILIZER RECOMMENDATION
# =========================================================

@router.post("/recommend")
def fertilizer_recommendation(
    data: FertilizerInput
):

    try:

        # -------------------------------------------------
        # PREPARE INPUT
        # -------------------------------------------------

        features = [

            float(data.nitrogen),

            float(data.phosphorus),

            float(data.potassium),

            float(data.ph),

            float(data.moisture),

            float(data.temperature)

        ]


        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        result = predict_fertilizer(
            features
        )


        # -------------------------------------------------
        # GET RECOMMENDED FERTILIZER
        # -------------------------------------------------

        fertilizer = result.get(
            "fertilizer"
        )

        accuracy = result.get(
            "accuracy",
            0
        )


        if not fertilizer:

            raise ValueError(
                "The fertilizer model did not return a fertilizer recommendation."
            )


        # -------------------------------------------------
        # GET ADVICE FROM DATASET
        # -------------------------------------------------

        advice = ""

        try:

            dataset = load_fertilizer_data()

            if (
                "recommended_fertilizer"
                in dataset.columns
                and
                "advice"
                in dataset.columns
            ):

                matching_rows = dataset[
                    dataset[
                        "recommended_fertilizer"
                    ]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    ==
                    str(fertilizer)
                    .strip()
                    .lower()
                ]

                if not matching_rows.empty:

                    advice_value = matching_rows[
                        "advice"
                    ].iloc[0]

                    if (
                        advice_value is not None
                        and
                        str(advice_value).strip()
                    ):

                        advice = str(
                            advice_value
                        ).strip()

        except Exception as advice_error:

            print(
                "Fertilizer advice lookup warning:",
                advice_error
            )


        # -------------------------------------------------
        # DEFAULT ADVICE
        # -------------------------------------------------

        if not advice:

            advice = (
                f"Use {fertilizer} according to "
                "the crop requirement and soil condition. "
                "Avoid excessive fertilizer application."
            )


        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {

            "status": "success",

            "recommended_fertilizer":
                str(fertilizer),

            "accuracy":
                round(
                    float(accuracy),
                    2
                ),

            "advice":
                advice

        }


    # =====================================================
    # VALID INPUT / MODEL ERROR
    # =====================================================

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        print(
            "Fertilizer recommendation error:",
            error
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Unable to generate fertilizer "
                "recommendation."
            )

        )