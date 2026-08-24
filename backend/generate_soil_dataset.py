import os
import numpy as np
import pandas as pd


# =========================================================
# SETTINGS
# =========================================================

TOTAL_ROWS = 9000

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dataset"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "soil_data.csv"
)

RANDOM_SEED = 42


# =========================================================
# RANDOM GENERATOR
# =========================================================

rng = np.random.default_rng(RANDOM_SEED)


# =========================================================
# GENERATE SOIL DATA
# =========================================================

rows = []


for _ in range(TOTAL_ROWS):

    # ---------------------------------------------
    # Generate realistic soil parameters
    # ---------------------------------------------

    nitrogen = rng.uniform(
        10,
        150
    )

    phosphorus = rng.uniform(
        5,
        100
    )

    potassium = rng.uniform(
        5,
        150
    )

    ph = rng.uniform(
        4.5,
        8.5
    )

    moisture = rng.uniform(
        10,
        80
    )

    temperature = rng.uniform(
        15,
        42
    )


    # =====================================================
    # SOIL HEALTH CLASSIFICATION
    # =====================================================

    healthy_score = 0
    poor_score = 0


    # ---------------------------------------------
    # Nitrogen
    # ---------------------------------------------

    if 60 <= nitrogen <= 120:
        healthy_score += 1

    elif nitrogen < 35 or nitrogen > 135:
        poor_score += 1


    # ---------------------------------------------
    # Phosphorus
    # ---------------------------------------------

    if 25 <= phosphorus <= 70:
        healthy_score += 1

    elif phosphorus < 15 or phosphorus > 85:
        poor_score += 1


    # ---------------------------------------------
    # Potassium
    # ---------------------------------------------

    if 30 <= potassium <= 100:
        healthy_score += 1

    elif potassium < 20 or potassium > 125:
        poor_score += 1


    # ---------------------------------------------
    # pH
    # ---------------------------------------------

    if 6.0 <= ph <= 7.5:
        healthy_score += 1

    elif ph < 5.2 or ph > 8.0:
        poor_score += 1


    # ---------------------------------------------
    # Moisture
    # ---------------------------------------------

    if 35 <= moisture <= 65:
        healthy_score += 1

    elif moisture < 20 or moisture > 75:
        poor_score += 1


    # ---------------------------------------------
    # Temperature
    # ---------------------------------------------

    if 20 <= temperature <= 32:
        healthy_score += 1

    elif temperature < 17 or temperature > 38:
        poor_score += 1


    # =====================================================
    # FINAL CLASS
    # =====================================================

    if healthy_score >= 4 and poor_score <= 1:

        soil_health = "Healthy"

    elif poor_score >= 3:

        soil_health = "Poor"

    else:

        soil_health = "Moderate"


    rows.append({
        "nitrogen": round(nitrogen, 2),
        "phosphorus": round(phosphorus, 2),
        "potassium": round(potassium, 2),
        "ph": round(ph, 2),
        "moisture": round(moisture, 2),
        "temperature": round(temperature, 2),
        "soil_health": soil_health
    })


# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(rows)


# =========================================================
# CREATE DATASET DIRECTORY
# =========================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================================================
# SAVE DATASET
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# DISPLAY INFORMATION
# =========================================================

print("=" * 50)
print("SOIL DATASET GENERATED")
print("=" * 50)

print(
    "Dataset records:",
    len(df)
)

print(
    "Columns:",
    df.columns.tolist()
)

print()
print("Soil health distribution:")

print(
    df["soil_health"].value_counts()
)

print()
print(
    "Saved to:",
    OUTPUT_FILE
)

print("=" * 50)