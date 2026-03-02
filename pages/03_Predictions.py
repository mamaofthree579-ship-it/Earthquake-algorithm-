import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime

st.title("Harmonic Stress Risk Model")

# ---- live USGS ----
today = date.today()
start = (today - timedelta(days=7)).isoformat()
end = today.isoformat()
data = requests.get(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    params={"format":"geojson","starttime":start,"endtime":end},
    headers={"User-Agent":"eq-demo"},
    timeout=15
).json()

rows = []
for f in data["features"]:
    p = f["properties"]
    rows.append({
        "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
        "place": p["place"],
        "mag": p["mag"] or 0
    })
df = pd.DataFrame(rows)
if df.empty:
    st.write("No quakes in window")
    st.stop()

# ---- cosmic forcing (flare proxy) ----
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {item["begin_time"][:10] for item in flares}
df["flare"] = df["date"].isin(flare_days).astype(int)

# parameters (tune these)
alpha, beta, gamma = 0.6, 0.0, 0.0
delta, lam, k, I_c = 0.4, 0.3, 1.0, 0.5
M0 = 1.0

# stress harmonic proxy (sum of last 3 mags with sin)
df["S_t"] = df["mag"].rolling(3, min_periods=1).apply(
    lambda x: np.sum(x * np.sin(np.arange(len(x)))), raw=False
)

# weakening amplifier (flare as magnetosphere proxy)
df["W"] = 1 + lam * (M0 - df["flare"]) / M0

# cosmic term
df["C"] = alpha * df["flare"]

# instability
df["I"] = df["W"] * df["S_t"] + delta * df["C"]

# logistic probability
df["P"] = 1 / (1 + np.exp(-k * (df["I"] - I_c)))

# classify
def level(p):
    if p < 0.25: return "Low"
    if p < 0.5: return "Moderate"
    if p < 0.75: return "Elevated"
    return "Critical"

df["Risk"] = df["P"].apply(level)

st.dataframe(df[["date","place","mag","flare","P","Risk"]])
