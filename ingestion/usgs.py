import requests
import pandas as pd
import time

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_earthquakes(retries=3, timeout=10):
    for attempt in range(retries):
        try:
            r = requests.get(USGS_URL, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            
            records = []
            for feature in data["features"]:
                props = feature["properties"]
                coords = feature["geometry"]["coordinates"]

                if props["mag"] is None:
                    continue

                records.append({
                    "mag": float(props["mag"]),
                    "place": props["place"],
                    "time": props["time"],
                    "lat": coords[1],
                    "lon": coords[0],
                    "depth": coords[2]
                })

            df = pd.DataFrame(records)
            df = df.dropna(subset=["lat", "lon", "mag"])
            df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]
            return df

        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2)
