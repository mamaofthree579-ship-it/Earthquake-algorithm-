import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime

st.title("7-Day Quake Risk (flare + transfer)")

# ---- live USGS ----
today = date.today()
start = (today - timedelta(days=7)).isoformat()
end = today.isoformat()
raw = requests.get(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    params={"format":"geojson","starttime":start,"endtime":end},
    headers={"User-Agent":"eq-demo"},
    timeout=15
).json()

rows = []
for f in raw["features"]:
    p = f["properties"]
    g = f["geometry"]["coordinates"]
    rows.append({
        "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
        "place": p["place"],
        "mag": p["mag"] or 0,
        "lon": g[0],
        "lat": g[1]
    })
df = pd.DataFrame(rows)

# ---- flares ----
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {i["begin_time"][:10] for i in flares}
df["flare"] = df["date"].isin(flare_days).astype(int)

# ---- transfer boost ----
if not df.empty:
    recent = df.nlargest(1, "mag").iloc[0]
    def hav(a,b):
        # km approx
        return 6371 * math.acos(
            math.sin(a[0])*math.sin(b[0]) + math.cos(a[0])*math.cos(b[0])*math.cos(a[1]-b[1])
        )
    center = (math.radians(recent["lat"]), math.radians(recent["lon"]))
    df["transfer"] = df.apply(
        lambda r: (recent["mag"] / (hav(center, (math.radians(r["lat"]), math.radians(r["lon"])))+1)) * df["flare"].max(),
        axis=1
    )
else:
    df["transfer"] = 0

base = {"Alaska":0.9,"California":0.6,"Chile":0.8,"Japan":0.8,"Indonesia":0.9,"Greece":0.5,"Turkey":0.7,"Mexico":0.6}
def prob(r):
    key = next((k for k in base if k.lower() in str(r["place"]).lower()), None)
    region = base.get(key,0.3)
    return min(0.30*region + 0.25*r["flare"] + 0.25*r["transfer"] + 0.20, 1.0)

df["elevated_risk_prob"] = df.apply(prob, axis=1)
st.dataframe(df.nlargest(5,"elevated_risk_prob")[["date","place","mag","elevated_risk_prob"]])
