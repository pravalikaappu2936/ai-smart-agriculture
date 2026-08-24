def get_crop_advice(crop):

    recommendations = {

        "rice":
            "Suitable for warm conditions with adequate rainfall and water availability.",

        "maize":
            "Requires balanced nutrients, warm temperatures and moderate rainfall.",

        "chickpea":
            "Suitable for cool and relatively dry conditions with well-drained soil.",

        "kidneybeans":
            "Prefers moderate temperatures, good drainage and adequate moisture.",

        "pigeonpeas":
            "Suitable for warm conditions and moderate rainfall with well-drained soil.",

        "mothbeans":
            "Well suited to warm and relatively dry conditions with lower water requirements.",

        "mungbean":
            "Suitable for warm conditions with moderate moisture and good drainage.",

        "blackgram":
            "Performs well in warm conditions with moderate rainfall and moisture.",

        "lentil":
            "Suitable for cool growing conditions with moderate moisture.",

        "pomegranate":
            "Prefers warm, relatively dry conditions and well-drained soil.",

        "banana":
            "Requires warm temperatures, good moisture and adequate nutrients.",

        "mango":
            "Requires warm conditions and well-drained soil with adequate moisture.",

        "grapes":
            "Prefers warm conditions, good drainage and controlled irrigation.",

        "watermelon":
            "Requires warm temperatures, good sunlight and well-drained soil.",

        "muskmelon":
            "Prefers warm temperatures, good sunlight and moderate irrigation.",

        "apple":
            "Requires cooler temperatures and suitable well-drained soil.",

        "orange":
            "Prefers warm conditions, adequate moisture and well-drained soil.",

        "papaya":
            "Requires warm temperatures, adequate moisture and fertile well-drained soil.",

        "coconut":
            "Requires warm humid conditions with adequate rainfall and moisture.",

        "cotton":
            "Suitable for warm conditions with moderate rainfall and well-drained soil.",

        "jute":
            "Requires warm humid conditions and relatively high rainfall.",

        "coffee":
            "Prefers warm humid conditions, moderate rainfall and well-drained soil."
    }

    crop_name = (
        str(crop)
        .strip()
        .lower()
    )

    return recommendations.get(
        crop_name,
        "The recommended crop is suitable according to the trained agricultural model. Check local soil and weather conditions before planting."
    )