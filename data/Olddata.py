import requests, pandas as pd
from datetime import datetime
from pathlib import Path

def fetch_usgs(start, end, out_file):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}"
    )
    headers = {"User-Agent": "earthquake-demo-bot/1.0"}
    r = requests.get(url, headers=headers, timeout=15)
    print("status:", r.status_code)          # check this in your logs
    if r.status_code != 200:
        print("body:", r.text[:200])        # often an HTML error page
        return
    try:
        data = r.json()
    except Exception as e:
        print("JSON parse failed:", e)
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
    pd.DataFrame(rows).to_csv(out_file, index=False)
    print(f"saved {len(rows)} rows")

# run once locally:
fetch_usgs("2024-01-01", "2024-12-31", Path(__file__).parent / "sample_quakes.csv")
