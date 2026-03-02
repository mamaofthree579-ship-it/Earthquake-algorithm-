import requests
import pandas as pd
from tenacity import retry, stop_after_attempt

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

@retry(stop=stop_after_attempt(3))
def fetch_usgs_earthquakes():

    response = requests.get(USGS_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

    records = []

    for feature in data["features"]:

        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        if props["mag"] is None:
            continue

        records.append({
            "magnitude": props["mag"],
            "latitude": coords[1],
            "longitude": coords[0],
            "depth": coords[2],
            "place": props["place"]
        })

    return pd.DataFrame(records)
