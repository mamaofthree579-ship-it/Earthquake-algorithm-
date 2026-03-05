import requests
import pandas as pd

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


def fetch_usgs_earthquakes():

    try:
        r = requests.get(USGS_URL, timeout=10)
        r.raise_for_status()

        data = r.json()

        rows = []

        for feature in data["features"]:

            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]

            mag = props["mag"]

            # Skip invalid magnitudes
            if mag is None or mag < 0:
                continue

            rows.append({
                "place": props["place"],
                "magnitude": max(float(mag), 0.1),
                "longitude": coords[0],
                "latitude": coords[1],
                "depth": coords[2]
            })

        return pd.DataFrame(rows)

    except Exception:
        # Safe fallback dataset
        return pd.DataFrame({
            "place": [],
            "magnitude": [],
            "longitude": [],
            "latitude": [],
            "depth": []
        })
