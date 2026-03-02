import requests, pandas as pd
from datetime import datetime
from pathlib import Path

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {
    "format": "geojson",
    "starttime": "2024-01-01",
    "endtime": "2024-01-07",   # one week – safer test
}
r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"}, timeout=10)
print("status:", r.status_code)
print("content‑type:", r.headers.get("content-type"))
print(r.text[:300])  # see the first bit

# If you see JSON starting with { "type":"FeatureCollection"...
# then parsing will work:
data = r.json()
rows = []
for f in data["features"]:
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
out = Path("data/sample_quakes.csv")
out.parent.mkdir(exist_ok=True)
df.to_csv(out, index=False)
print(f"Wrote {len(df)} rows")
