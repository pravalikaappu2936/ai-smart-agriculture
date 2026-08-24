def get_fertilizer_advice(fertilizer):

    recommendations = {

        "Urea":
            "Nitrogen is relatively low. Urea can be applied to improve nitrogen availability and support vegetative growth.",

        "DAP":
            "DAP provides nitrogen and phosphorus. It can support root development and improve nutrient availability.",

        "NPK 10-10-10":
            "A balanced NPK fertilizer is recommended to maintain nitrogen, phosphorus, and potassium levels.",

        "NPK 10-26-26":
            "This fertilizer is higher in phosphorus and potassium and can support root development and overall crop growth.",

        "NPK 20-20-20":
            "A balanced higher-strength NPK fertilizer is recommended when nitrogen, phosphorus, and potassium requirements are relatively high.",

        "Potassium Sulphate":
            "Potassium sulphate can support potassium requirements and improve plant strength and crop quality. Avoid unnecessary application when potassium is already sufficient."
    }

    fertilizer = str(
        fertilizer
    ).strip()

    return recommendations.get(
        fertilizer,
        "No specific fertilizer advice is available for this prediction."
    )