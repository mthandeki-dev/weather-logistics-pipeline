import json
import os
from datetime import datetime
import requests
#ETL = Extract, Transform, Load
# Define a few major global logistics hubs (City: (Lat, Lon))
TARGET_CITIES = {
    "Rotterdam": (51.9244, 4.4777),
    "Singapore": (1.3521, 103.8198),
    "Shanghai": (31.2304, 121.4737),
    "Chicago": (41.8781, -87.6298),
    "Durban": (-29.8587, 31.0218),
}

# Create a local directory to hold the raw data if it doesn't exist
RAW_DATA_DIR = "./data/raw"
os.makedirs(RAW_DATA_DIR, exist_ok=True)


def extract_weather_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    failures = []

    for city, (lat, lon) in TARGET_CITIES.items():
        print(f"Fetching data for {city}...")

        # Open-Meteo API URL with parameters for current weather data
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "windspeed_unit": "kmh",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()

            # Add the city name to the payload for context later
            data["city_name"] = city

            # Save raw JSON to your local Linux directory
            filename = f"{RAW_DATA_DIR}/{city}_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)

            print(f"Successfully saved raw data to {filename}")

        except requests.RequestException as e:
            print(f"Failed to fetch data for {city}: {e}")
            failures.append(city)

    if failures:
        failed_cities = ", ".join(failures)
        raise RuntimeError(f"Weather extraction failed for: {failed_cities}")


if __name__ == "__main__":
    extract_weather_data()