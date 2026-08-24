def get_soil_recommendation(status):

    recommendations = {

        "Healthy":
            "Soil condition is healthy. "
            "Continue current farming practices "
            "and maintain balanced nutrient levels.",

        "Moderate":
            "Soil condition is moderate. "
            "Add organic manure or compost, "
            "monitor nutrient levels, "
            "and maintain suitable soil moisture.",

        "Poor":
            "Soil condition is poor. "
            "Improve soil nutrients using compost "
            "and balanced fertilizers. "
            "Regularly monitor pH, moisture and NPK levels."

    }

    return recommendations.get(

        status,

        "No recommendation available."

    )