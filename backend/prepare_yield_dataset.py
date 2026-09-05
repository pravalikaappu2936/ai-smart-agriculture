from pathlib import Path
import pandas as pd

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"

OUTPUT_FILE = DATASET_DIR / "crop_yield_data.csv"

DATASET_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# HUGGING FACE DATASET
# ---------------------------------------------------------
DATASET_URL = (
    "https://huggingface.co/datasets/"
    "dhyann2815/india-crop-yield-prediction/"
    "resolve/main/"
    "data/train-00000-of-00001.parquet"
)


# ---------------------------------------------------------
# DOWNLOAD / LOAD DATASET
# ---------------------------------------------------------
def load_dataset():

    print("=" * 60)
    print("CROP YIELD DATASET")
    print("=" * 60)

    print("\nDownloading/loading dataset...")

    try:
        df = pd.read_parquet(DATASET_URL)
    except Exception as error:
        print("\nFAILED TO LOAD DATASET")
        print(error)
        raise

    print(f"\nOriginal records: {len(df)}")

    print("\nOriginal columns:")
    print(list(df.columns))

    return df


# ---------------------------------------------------------
# CLEAN
# ---------------------------------------------------------
def clean_dataset(df):

    print("\nCleaning dataset...")

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    required_columns = [
        "year",
        "state",
        "crop",
        "season",
        "area",
        "production",
        "annual_rainfall",
        "fertilizer",
        "pesticide",
        "yield",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        print("\nMissing columns:")
        print(missing)

        print("\nAvailable columns:")
        print(list(df.columns))

        raise ValueError(
            "Required crop-yield columns are missing."
        )

    # Numeric columns
    numeric_columns = [
        "year",
        "area",
        "production",
        "annual_rainfall",
        "fertilizer",
        "pesticide",
        "yield",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # String columns
    string_columns = [
        "state",
        "crop",
        "season",
    ]

    for column in string_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    # Remove missing values
    df = df.dropna(
        subset=numeric_columns + string_columns
    )

    # Remove invalid values
    df = df[
        (df["year"] >= 2000)
        & (df["year"] <= 2100)
        & (df["area"] > 0)
        & (df["production"] >= 0)
        & (df["annual_rainfall"] >= 0)
        & (df["fertilizer"] >= 0)
        & (df["pesticide"] >= 0)
        & (df["yield"] >= 0)
    ]

    # Remove duplicates
    df = df.drop_duplicates()

    print(
        f"Records after cleaning: {len(df)}"
    )

    return df


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
def save_dataset(df):

    columns = [
        "year",
        "state",
        "crop",
        "season",
        "area",
        "production",
        "annual_rainfall",
        "fertilizer",
        "pesticide",
        "yield",
    ]

    df = df[columns]

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("CROP YIELD DATASET READY")
    print("=" * 60)

    print(f"File: {OUTPUT_FILE}")
    print(f"Records: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nStates:")
    print(df["state"].nunique())

    print("\nCrops:")
    print(df["crop"].nunique())

    print("\nSeasons:")
    print(df["season"].nunique())

    print("\nFirst 5 records:")
    print(df.head())

    print("=" * 60)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():

    df = load_dataset()

    df = clean_dataset(df)

    save_dataset(df)


if __name__ == "__main__":
    main()