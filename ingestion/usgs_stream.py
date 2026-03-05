import requests
import pandas as pd

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_usgs_earthquakes():

    r = requests.get(USGS_URL, timeout=10)
    data = r.json()

    rows = []

    for feature in data["features"]:

        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        rows.append({
            "place": props["place"],
            "magnitude": props["mag"],
            "longitude": coords[0],
            "latitude": coords[1],
            "depth": coords[2]
        })

    df = pd.DataFrame(rows)

    return df
