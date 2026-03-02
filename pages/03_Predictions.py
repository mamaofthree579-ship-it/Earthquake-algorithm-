import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from sklearn.linear_model import LogisticRegression

st.title("Trained Harmonic Stress Risk Model")

today = date.today()
start_hist = (today - timedelta(days=90)).isoformat()
start_recent = (today - timedelta(days=7)).isoformat()
end = today.isoformat()

def fetch(start, end, minmag=None):
    try:
        params = {
            "format": "geojson",
            "starttime": f"{start}T00:00:00",
            "endtime": f"{end}T23:59:59"
        }
        if minmag is not None:
            params["minmagnitude"] = minmag
        r = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            params=params,
            headers={"User-Agent": "eq-demo"},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        st.warning(f"USGS request failed: {e}")
        return pd.DataFrame()
    rows = []
    for f in data.get("features", []):
        p = f["properties"]
        rows.append({
            "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
            "place": p["place"],
            "mag": p["mag"] or 0
        })
    return pd.DataFrame(rows)

df_hist = fetch(start_hist, start_recent, minmag=4)
df = fetch(start_recent, end)

if df.empty:
    st.write("No recent quakes")
    st.stop()

flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {item["begin_time"][:10] for item in flares}

for frame in (df_hist, df):
    if frame.empty:
        continue
    frame["flare"] = frame["date"].isin(flare_days).astype(int)
    frame["S_t"] = frame["mag"].rolling(3, min_periods=1).apply(
        lambda x: np.sum(x * np.sin(np.arange(len(x)))), raw=False
    )
    frame["W"] = 1 + 0.3 * (1 - frame["flare"])
    frame["C"] = 0.6 * frame["flare"]

if not df_hist.empty:
    df_hist["target"] = (df_hist["mag"] >= 5).astype(int)
    X = df_hist[["S_t", "C", "W"]].fillna(0)
    y = df_hist["target"]
    model = LogisticRegression().fit(X, y)
    coef_S, coef_C, coef_W = model.coef_[0]
    intercept = model.intercept_[0]
else:
    coef_S, coef_C, coef_W, intercept = 1.0, 0.4, 0.3, -0.5

df["I"] = coef_W * df["W"] * df["S_t"] + coef_C * df["C"]
df["P"] = 1 / (1 + np.exp(-(df["I"] + intercept)))
df["Risk"] = df["P"].apply(
    lambda p: "Low" if p < 0.25 else "Moderate" if p < 0.5 else "Elevated" if p < 0.75 else "Critical"
)

st.subheader("Recent risk")
st.dataframe(df[["date", "place", "mag", "P", "Risk"]])

last_I = df["I"].iloc[-1]
future = []
for i in range(1, 4):
    d = (today + timedelta(days=i)).isoformat()
    P_fut = 1 / (1 + math.exp(-(last_I + intercept)))
    future.append({
        "date": d,
        "P": P_fut,
        "Risk": "Low" if P_fut < 0.25 else "Moderate" if P_fut < 0.5 else "Elevated" if P_fut < 0.75 else "Critical"
    })
st.subheader("Forward risk")
st.dataframe(pd.DataFrame(future))
