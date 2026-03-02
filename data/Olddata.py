import requests, pandas as pd
from datetime import datetime
from pathlib import Path

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {"format": "geojson", "starttime": "2024-01-01", "endtime": "2024-01-02"}
print("Requesting…")
r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"}, timeout=15)
print("HTTP", r.status_code)
print("Content-type:", r.headers.get("content-type"))

# bail out early if not JSON
if "application/json" not in r.headers.get("content-type", ""):
    print("Got non‑JSON, body preview:")
    print(r.text[:300])
    raise SystemExit

raw = r.json()
print("Count in metadata:", raw.get("metadata", {}).get("count"))

rows = []
for f in raw.get("features", []):
    p = f["properties"]
    t = datetime.utcfromtimestamp(p["time"] / 1000.0)
    rows.append({
        "date": t.strftime("%Y-%m-%d"),
        "time": t.strftime("%H:%M:%S"),
        "place": p["place"],
        "magnitude": p["mag"] or 0,
        "solar_flare_window": 0
    })

print("Rows built:", len(rows))
df = pd.DataFrame(rows)
out = Path("data/sample_quakes.csv")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print("Wrote CSV to", out.resolve())
