# =========================================================
# CROP IRRIGATION WATER FACTORS
# =========================================================

CROP_WATER_FACTOR = {

    # -----------------------------------------------------
    # ORIGINAL CROPS
    # -----------------------------------------------------

    "rice": 1.30,
    "maize": 1.00,
    "chickpea": 0.75,
    "cotton": 1.10,
    "wheat": 0.90,
    "groundnut": 0.85,
    "banana": 1.25,

    # -----------------------------------------------------
    # ADDITIONAL CROPS
    # -----------------------------------------------------

    "sugarcane": 1.25,
    "tomato": 1.15,
    "potato": 1.05,
    "onion": 0.95,
    "turmeric": 1.00,
    "chilli": 0.95,
    "sorghum": 0.75,
    "millet": 0.65,
    "ragi": 0.70,
    "soybean": 0.90,
    "pigeon_pea": 0.75,
    "okra": 1.00,
    "cabbage": 1.00,
    "carrot": 0.90,
}


# =========================================================
# CROP ALIASES
# =========================================================

CROP_ALIASES = {

    # Pigeon pea
    "pigeonpea": "pigeon_pea",
    "pigeon pea": "pigeon_pea",
    "pigeon-pea": "pigeon_pea",

    # Groundnut
    "ground nut": "groundnut",
    "ground-nut": "groundnut",

    # Chilli
    "chili": "chilli",
    "chilli pepper": "chilli",

    # Chickpea
    "chick pea": "chickpea",
    "chick-pea": "chickpea",

    # Sugarcane
    "sugar cane": "sugarcane",
    "sugar-cane": "sugarcane",

    # Soybean
    "soy bean": "soybean",
    "soy-bean": "soybean",

    # Maize
    "corn": "maize",

    # Ragi
    "ragi millet": "ragi",
}


# =========================================================
# NORMALIZE CROP
# =========================================================

def normalize_crop(crop_type: str) -> str:

    if not crop_type:
        raise ValueError(
            "Crop type is required."
        )

    crop = str(crop_type).strip().lower()

    # Remove unnecessary spaces
    crop = " ".join(crop.split())

    # Check aliases
    if crop in CROP_ALIASES:

        crop = CROP_ALIASES[crop]

    # Convert hyphen to underscore
    crop = crop.replace("-", "_")

    # Check again after conversion
    if crop in CROP_ALIASES:

        crop = CROP_ALIASES[crop]

    # Validate
    if crop not in CROP_WATER_FACTOR:

        raise ValueError(
            f"Unsupported crop type: {crop_type}. "
            f"Supported crops: "
            f"{', '.join(CROP_WATER_FACTOR.keys())}"
        )

    return crop


# =========================================================
# GET CROP WATER FACTOR
# =========================================================

def get_crop_water_factor(
    crop_type: str
) -> float:

    crop = normalize_crop(
        crop_type
    )

    return CROP_WATER_FACTOR[crop]