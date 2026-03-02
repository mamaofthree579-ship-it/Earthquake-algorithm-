import requests, pandas as pd
from datetime import datetime
from pathlib import Path

def pull_data(start, end):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": start, "endtime": end}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"})
    r.raise_for_status()
    return r.json()

def to_csv(raw, out_path):
    rows = []
    for f in raw["features"]:
        p = f["properties"]
        t = datetime.utcfromtimestamp(p["time"] / 1000.0)
        rows.append({
            "date": t.strftime("%Y-%m-%d"),
            "time": t.strftime("%H:%M:%S"),
            "place": p["place"],
            "magnitude": p["mag"] or 0,
            "solar_flare_window": 0
        })
    df = pd.DataFrame(rows)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return df

# ---- run it ----
raw = pull_data("2024-01-01", "2024-01-07")
df = to_csv(raw, "data/sample_quakes.csv")
print(df.head())
print(f"Saved {len(df)} rows")
