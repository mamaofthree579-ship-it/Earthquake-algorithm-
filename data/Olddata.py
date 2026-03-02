# pages/02_Load_Data.py
import streamlit as st
import requests, pandas as pd
from datetime import datetime
from pathlib import Path

st.title("Fetch USGS → CSV")

# force ASCII hyphen, add time to be safe
start = st.text_input("Start", "2024-01-01T00:00:00")
end   = st.text_input("End",   "2024-01-07T23:59:59")

if st.button("Run"):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {"format": "geojson", "starttime": start, "endtime": end}
    r = requests.get(url, params=params, headers={"User-Agent": "eq-demo"}, timeout=15)
    st.write("status:", r.status_code)
    if r.status_code != 200:
        st.error(r.text[:200])
        st.stop()

    raw = r.json()
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
    out = Path("data/sample_quakes.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    st.success(f"Wrote {len(df)} rows")
    st.dataframe(df.head(20))  # show 20 rows
# after df built
flares_resp = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
)
flares_resp.raise_for_status()
flares = flares_resp.json()

flare_dates = {item["begin_time"][:10] for item in flares}  # extract YYYY‑MM‑DD
df["solar_flare_window"] = df["date"].isin(flare_dates).astype(int)
# or
st.write(df.shape)         # (1000, 5) confirms 1000 rows, 5 columns
