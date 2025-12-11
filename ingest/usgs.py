"""
USGS ingestion adapter (GeoJSON weekly summary).
Provides a function to fetch and normalize the all-week feed into a DataFrame.
"""
import requests
import pandas as pd
from datetime import datetime

USGS_WEEK_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"

def fetch_usgs_week(timeout=10):
    r = requests.get(USGS_WEEK_URL, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    features = data.get("features", [])
    records = []
    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {}) or {}
        coords = geom.get("coordinates", [None, None, None])
        records.append({
            "id": f.get("id"),
            "time_utc": datetime.utcfromtimestamp(props.get("time", 0) / 1000),
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2] if len(coords) > 2 else None,
            "url": props.get("url")
        })
    return pd.DataFrame.from_records(records)
