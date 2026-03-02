import streamlit as st
import requests, pandas as pd, numpy as np
from datetime import date, timedelta, datetime

st.title("7‑Day Quake Predictions (live)")

# ---- live USGS (last 7 days) ----
today = date.today()
start = (today - timedelta(days=7)).isoformat()
end = today.isoformat()
resp = requests.get(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    params={"format":"geojson","starttime":start,"endtime":end},
    headers={"User-Agent":"eq-demo"},
    timeout=15
)
resp.raise_for_status()
raw = resp.json()
rows = [{
    "date": datetime.utcfromtimestamp(f["properties"]["time"]/1000).strftime("%Y-%m-%d"),
    "place": f["properties"]["place"],
    "magnitude": f["properties"]["mag"] or 0
} for f in raw["features"]]
df = pd.DataFrame(rows)

# ---- live flares ----
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_dates = {item["begin_time"][:10] for item in flares}
df["solar_flare_window"] = df["date"].isin(flare_dates).astype(int)

# ---- same PIN model ----
base_rates = {"Alaska":0.9,"California":0.6,"Chile":0.8,"Japan":0.8,
              "Indonesia":0.9,"Greece":0.5,"Turkey":0.7,"Mexico":0.6}
w_region,w_flare,w_quant,w_day,w_bias = 0.30,0.25,0.25,0.10,0.05
df["magnitude"] = pd.to_numeric(df["magnitude"],errors="coerce").fillna(0)
quant = df["magnitude"].rank(pct=True)
df["elevated_risk_prob"] = df.apply(
    lambda r: min(w_region*base_rates.get(
        next((k for k in base_rates if k.lower() in str(r["place"]).lower()), 0.3)
    + w_flare*r["solar_flare_window"] + w_quant*quant[r.name] + w_bias, 1.0),
    axis=1
)
top = df.nlargest(5,"elevated_risk_prob")[["date","place","magnitude","solar_flare_window","elevated_risk_prob"]]
st.dataframe(top)
