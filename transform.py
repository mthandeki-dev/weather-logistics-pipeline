import glob
import json
import os
import pandas as pd

RAW_DATA_DIR = "./data/raw"
PROCESSED_DATA_DIR = "./data/processed"
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def determine_risk(row):
    """Business logic to flag weather-related logistics risks."""
    # Flag high wind or high precipitation as a delayed risk
    if row["wind_speed"] > 40.0 or row["precipitation"] > 5.0:
        return "Delayed"
    return "Clear"


def transform_raw_data():
    # Find all JSON files in the raw data directory
    json_files = glob.glob(f"{RAW_DATA_DIR}/*.json")

    if not json_files:
        raise FileNotFoundError(
            f"No raw data files found in {RAW_DATA_DIR}. Run extract.py first."
        )

    all_records = []

    for file_path in json_files:
        with open(file_path, "r") as f:
            raw_data = json.load(f)

        # Open-Meteo nests current weather details inside 'current_weather'
        current = raw_data.get("current_weather", {})

        # Build a flat dictionary structure
        record = {
            "city": raw_data.get("city_name"),
            "latitude": raw_data.get("latitude"),
            "longitude": raw_data.get("longitude"),
            "temperature": current.get("temperature"),
            "wind_speed": current.get("windspeed"),
            "precipitation": current.get(
                "precipitation", 0.0
            ),  # Default to 0 if not present
            "checked_at": current.get("time"),
        }
        all_records.append(record)

    # Convert our list of dictionaries into a clean DataFrame
    df = pd.DataFrame(all_records)

    # Apply our engineering rule to create a new calculated column
    df["transport_status"] = df.apply(determine_risk, axis=1)

    # Save to a clean CSV file
    output_file = f"{PROCESSED_DATA_DIR}/clean_logistics_data.csv"
    df.to_csv(output_file, index=False)
    print(
        f"Transformation complete! Processed {len(df)} records into {output_file}"
    )


if __name__ == "__main__":
    transform_raw_data()