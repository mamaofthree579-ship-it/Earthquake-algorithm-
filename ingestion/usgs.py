import requests
import pandas as pd

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_earthquakes():
    r = requests.get(USGS_URL)
    data = r.json()
    
    records = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        
        records.append({
            "mag": props["mag"],
            "place": props["place"],
            "time": props["time"],
            "lat": coords[1],
            "lon": coords[0],
            "depth": coords[2]
        })
    
    return pd.DataFrame(records)
