import numpy as np
import shap


# =========================================================
# FEATURE NAMES
# =========================================================

FEATURE_NAMES = [

    "Nitrogen",

    "Phosphorus",

    "Potassium",

    "pH",

    "Moisture",

    "Temperature"
]


# =========================================================
# DESCRIPTIONS
# =========================================================

FEATURE_DESCRIPTIONS = {

    "Nitrogen":
        "Nitrogen level in the soil.",

    "Phosphorus":
        "Phosphorus level in the soil.",

    "Potassium":
        "Potassium level in the soil.",

    "pH":
        "Soil acidity or alkalinity.",

    "Moisture":
        "Amount of water present in the soil.",

    "Temperature":
        "Current soil temperature."
}


# =========================================================
# IMPACT LABEL
# =========================================================

def get_impact_label(value):

    if value >= 0.20:

        return "Very High Impact"

    elif value >= 0.10:

        return "High Impact"

    elif value >= 0.05:

        return "Moderate Impact"

    else:

        return "Low Impact"


# =========================================================
# GENERATE EXPLANATION
# =========================================================

def generate_explanation(
    features,
    model=None
):

    values = np.array(
        features[0],
        dtype=float
    )

    if len(values) != len(
        FEATURE_NAMES
    ):

        raise ValueError(
            "Invalid number of soil features."
        )

    explanation = []

    # =====================================================
    # SHAP
    # =====================================================

    if model is not None:

        try:

            explainer = shap.TreeExplainer(
                model
            )

            shap_values = (
                explainer.shap_values(
                    values.reshape(1, -1)
                )
            )

            # ------------------------------------------------
            # SHAP compatibility
            # ------------------------------------------------

            if isinstance(
                shap_values,
                list
            ):

                shap_array = np.mean(
                    np.abs(
                        np.asarray(
                            shap_values
                        )
                    ),
                    axis=0
                )[0]

            else:

                shap_array = np.asarray(
                    shap_values
                )

                if shap_array.ndim == 3:

                    shap_array = np.mean(
                        np.abs(
                            shap_array
                        ),
                        axis=2
                    )[0]

                elif shap_array.ndim == 2:

                    shap_array = np.abs(
                        shap_array[0]
                    )

                else:

                    shap_array = np.abs(
                        shap_array
                    )

            # ------------------------------------------------
            # Build explanation
            # ------------------------------------------------

            for index, value in enumerate(
                values
            ):

                importance = float(
                    shap_array[index]
                )

                feature_name = (
                    FEATURE_NAMES[index]
                )

                explanation.append({

                    "feature":
                        feature_name,

                    "value":
                        float(value),

                    "impact":
                        get_impact_label(
                            importance
                        ),

                    "importance":
                        round(
                            importance,
                            6
                        ),

                    "description":
                        FEATURE_DESCRIPTIONS[
                            feature_name
                        ]
                })

            # ------------------------------------------------
            # Sort by importance
            # ------------------------------------------------

            explanation.sort(

                key=lambda item:
                    item["importance"],

                reverse=True
            )

            return {

                "method":
                    "SHAP - Random Forest",

                "features":
                    explanation
            }

        except Exception as error:

            print(
                "SHAP explanation error:",
                error
            )

    # =====================================================
    # FALLBACK
    # =====================================================

    for index, value in enumerate(
        values
    ):

        feature_name = (
            FEATURE_NAMES[index]
        )

        explanation.append({

            "feature":
                feature_name,

            "value":
                float(value),

            "impact":
                "Available",

            "importance":
                0,

            "description":
                FEATURE_DESCRIPTIONS[
                    feature_name
                ]
        })

    return {

        "method":
            "Feature-based explanation",

        "features":
            explanation
    }