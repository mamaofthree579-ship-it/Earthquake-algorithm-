import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

def fetch_usgs(start, end, out_file):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}"
    )
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "eq-demo"})
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"USGS request failed: {e}")
        return

    rows = []
    for f in data["features"]:
        p = f["properties"]
        t = datetime.utcfromtimestamp(p["time"] / 1000.0)
        rows.append({
            "date": t.strftime("%Y-%m-%d"),
            "time": t.strftime("%H:%M:%S"),
            "place": p["place"],
            "magnitude": p["mag"] if p["mag"] is not None else 0,
            "solar_flare_window": 0
        })

    df = pd.DataFrame(rows)
    out_path = Path(out_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")

# example run
fetch_usgs("2023-01-01", "2023-12-31", "data/sample_quakes.csv")
