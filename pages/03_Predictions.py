import streamlit as st
import requests, pandas as pd, numpy as np
from datetime import date, timedelta, datetime

st.title("7-Day Quake Predictions (live)")

# after calculating start/end
st.caption(f"Window: {start} → {end} (today is {date.today()})")

# ---- live USGS (last 7 days) ----
today = date.today()
start = (today - timedelta(days=7)).isoformat()
end = today.isoformat()
resp = requests.get(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    params={"format": "geojson", "starttime": start, "endtime": end},
    headers={"User-Agent": "eq-demo"},
    timeout=15
)
resp.raise_for_status()
raw = resp.json()
rows = []
for f in raw["features"]:
    p = f["properties"]
    t = datetime.utcfromtimestamp(p["time"] / 1000)
    rows.append({
        "date": t.strftime("%Y-%m-%d"),
        "place": p["place"],
        "magnitude": p["mag"] or 0
    })
df = pd.DataFrame(rows)

# ---- live flares ----
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_dates = {item["begin_time"][:10] for item in flares}
df["solar_flare_window"] = df["date"].isin(flare_dates).astype(int)

# ---- model ----
base_rates = {"Alaska":0.9,"California":0.6,"Chile":0.8,"Japan":0.8,
              "Indonesia":0.9,"Greece":0.5,"Turkey":0.7,"Mexico":0.6}
w_region, w_flare, w_quant, w_bias = 0.30, 0.25, 0.25, 0.20
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0)
quant = df["magnitude"].rank(pct=True)

def prob_row(r):
    key = next((k for k in base_rates if k.lower() in str(r["place"]).lower()), None)
    region = base_rates.get(key, 0.3)
    return min(w_region*region + w_flare*r["solar_flare_window"] + w_quant*quant[r.name] + w_bias, 1.0)

df["elevated_risk_prob"] = df.apply(prob_row, axis=1)
top = df.nlargest(5, "elevated_risk_prob")[["date","place","magnitude","solar_flare_window","elevated_risk_prob"]]
st.dataframe(top)
