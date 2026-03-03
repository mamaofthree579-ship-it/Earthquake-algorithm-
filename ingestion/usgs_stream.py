import requests
import pandas as pd
from tenacity import retry, stop_after_attempt

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

@retry(stop=stop_after_attempt(3))
def fetch_usgs_stream():

    response = requests.get(USGS_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

    records = []

    for feature in data.get("features", []):

        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])

        if len(coords) < 2 or props.get("mag") is None:
            continue

        records.append({
            "longitude": coords[0],
            "latitude": coords[1],
            "depth": coords[2] if len(coords) > 2 else 0,
            "magnitude": props.get("mag"),
            "place": props.get("place","")
        })

    return pd.DataFrame(records)
