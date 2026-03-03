import requests
import pandas as pd

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_usgs_stream():

    try:
        response = requests.get(USGS_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        records = []

        for feature in data.get("features", []):

            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            if len(coords) < 2:
                continue

            records.append({
                "longitude": coords[0],
                "latitude": coords[1],
                "magnitude": props.get("mag", 0)
            })

        return pd.DataFrame(records)

    except Exception:
        return pd.DataFrame()
