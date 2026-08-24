def get_irrigation_advice(irrigation_status):

    recommendations = {

        "Low Irrigation":
            "Soil moisture is adequate. Only a small amount of irrigation may be required.",

        "Moderate Irrigation":
            "Provide moderate irrigation and monitor soil moisture regularly.",

        "High Irrigation":
            "Additional irrigation may be required. Check soil moisture and rainfall conditions."

    }

    return recommendations.get(

        irrigation_status,

        "No irrigation recommendation available."

    )