import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

def fetch_and_save(start, end, out_file):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": start, "endtime": end}
    headers = {"User-Agent": "eq-demo"}

    r = requests.get(url, params=params, headers=headers, timeout=15)
    print("status:", r.status_code)
    if r.status_code != 200:
        print("response:", r.text[:200])
        return

    raw = r.json() # <-- correct place, right after a successful request

    rows = []
    for f in raw.get("features", []):
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
    print(f"Saved {len(df)} rows to {out_path}")

# ---- run it ----
fetch_and_save("2024-01-01", "2024-01-07", "data/sample_quakes.csv")
