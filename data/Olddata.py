import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

st.title("Old Data Builder")

# ---- fetch USGS quakes ----
try:
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": "2024-01-01", "endtime": "2024-01-07"}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"}, timeout=15)
    r.raise_for_status()
    raw = r.json()
except Exception as e:
    st.error(f"USGS fetch failed: {e}")
    st.stop()

rows = []
for f in raw["features"]:
    p = f["properties"]
    t = datetime.utcfromtimestamp(p["time"] / 1000.0)
    rows.append({
        "date": t.strftime("%Y-%m-%d"),
        "time": t.strftime("%H:%M:%S"),
        "place": p["place"],
        "magnitude": p["mag"] or 0,
    })

df = pd.DataFrame(rows)

# ---- NOAA flare integration ----
try:
    flares_resp = requests.get(
        "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
        timeout=15
    )
    flares_resp.raise_for_status()
    flares = flares_resp.json()
    flare_dates = {item["begin_time"][:10] for item in flares}
    df["solar_flare_window"] = df["date"].isin(flare_dates).astype(int)
except Exception as e:
    st.warning(f"Flare fetch failed, using zeros: {e}")
    df["solar_flare_window"] = 0

# ---- write CSV ----
out = Path("data/sample_quakes.csv")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

st.success(f"Wrote {len(df)} rows to {out}")
st.write("Columns:", df.columns.tolist())
st.dataframe(df.head(10))
