import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime

st.title("Harmonic Stress Model + Forward Risk")

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
    rows.append({
        "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
        "place": p["place"],
        "mag": p["mag"] or 0
    })
df = pd.DataFrame(rows)
if df.empty:
    st.write("No quakes")
    st.stop()

# ---- cosmic forcing ----
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {i["begin_time"][:10] for i in flares}
df["flare"] = df["date"].isin(flare_days).astype(int)

# params
alpha,delta,lam,k,I_c = 0.6,0.4,0.3,1.0,0.5
M0 = 1.0

df["S_t"] = df["mag"].rolling(3,min_periods=1).apply(lambda x: np.sum(x*np.sin(np.arange(len(x)))), raw=False)
df["W"] = 1 + lam * (M0 - df["flare"]) / M0
df["C"] = alpha * df["flare"]
df["I"] = df["W"] * df["S_t"] + delta * df["C"]
df["P"] = 1 / (1 + np.exp(-k * (df["I"] - I_c)))

def level(p):
    return "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical"

df["Risk"] = df["P"].apply(level)

# ---- forward projection ----
last_I = df["I"].iloc[-1]
future = []
for i in range(1,4):
    d = (today + timedelta(days=i)).isoformat()
    P_fut = 1 / (1 + math.exp(-k * (last_I - I_c)))
    future.append({"date":d, "place":"—", "mag":"—", "flare":"—", "P":P_fut, "Risk":level(P_fut)})
fut = pd.DataFrame(future)

st.subheader("History")
st.dataframe(df[["date","place","mag","flare","P","Risk"]])
st.subheader("Forward risk (next 3 days)")
st.dataframe(fut)
