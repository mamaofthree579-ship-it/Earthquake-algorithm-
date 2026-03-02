import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from sklearn.linear_model import LogisticRegression

st.title("Trained Harmonic Stress Risk Model")

# ----- physics constants -----
mu_v, kappa_v, eta_v = 0.5, 0.1, 0.05
D, rho, crit_k = 0.3, 0.2, 0.1

# ----- upload with validation -----
uploaded = st.file_uploader("Upload past quakes CSV (date,mag,place)", type="csv")
if uploaded:
    df_hist = pd.read_csv(uploaded)
    # normalize column names
    df_hist.columns = df_hist.columns.str.lower().str.strip()
    # require mag; if missing, warn and empty
    if "mag" not in df_hist.columns or "date" not in df_hist.columns:
        st.warning("CSV must include 'date' and 'mag' columns")
        df_hist = pd.DataFrame()
    else:
        if "place" not in df_hist.columns:
            df_hist["place"] = "unknown"
        df_hist["date"] = pd.to_datetime(df_hist["date"]).dt.strftime("%Y-%m-%d")
else:
    df_hist = pd.DataFrame()

today = date.today()
end = today.isoformat()
start_recent = (today - timedelta(days=7)).isoformat()

def fetch(start, end):
    try:
        r = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            params={"format":"geojson",
                    "starttime":f"{start}T00:00:00",
                    "endtime":f"{end}T23:59:59"},
            headers={"User-Agent":"eq-demo"},
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

df = fetch(start_recent, end)
if df.empty:
    st.write("No recent quakes")
    st.stop()

flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {item["begin_time"][:10] for item in flares}

# process both frames
frames = []
for frame in (df_hist, df):
    if frame.empty:
        continue
    frame = frame.copy()
    frame["flare"] = frame["date"].isin(flare_days).astype(int)
    frame["S_t"] = frame["mag"].rolling(3, min_periods=1).apply(
        lambda x: np.sum(x*np.sin(np.arange(len(x)))), raw=False
    )
    frame["P_v"] = 0.0
    for i in range(1, len(frame)):
        q = frame["flare"].iloc[i] * frame["mag"].iloc[i]
        dp = kappa_v * q - eta_v * frame["P_v"].iloc[i-1]
        frame["P_v"].iloc[i] = frame["P_v"].iloc[i-1] + dp
    frame["W"] = 1 + 0.3 * (1 - frame["flare"])
    frame["C"] = 0.6 * frame["flare"]
    frames.append(frame)

if len(frames)==2:
    df_hist, df = frames
else:
    df = frames[0]

if not df_hist.empty:
    df_hist["target"] = (df_hist["mag"] >= 5).astype(int)
    X = df_hist[["S_t","C","W","P_v"]].fillna(0)
    y = df_hist["target"]
    model = LogisticRegression().fit(X, y)
    coef = model.coef_[0]
    intercept = model.intercept_[0]
else:
    coef = np.array([1.0, 0.4, 0.3, mu_v])
    intercept = 0.0

df["I_raw"] = (coef[3]*df["P_v"] + coef[2]*df["W"]*df["S_t"] + coef[1]*df["C"])
df["I"] = df["I_raw"].rolling(3, min_periods=1).mean() - rho*df["I_raw"]
F_total = df["W"]*df["S_t"] + df["C"] + mu_v*df["P_v"]
F_crit = rho + D*(crit_k**2)
df["Unstable"] = F_total > F_crit
df["P"] = 1 / (1 + np.exp(-(df["I"] + intercept)))
df["P"] = df["P"].clip(0.01, 0.99)
df["Risk"] = df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")
df["Risk"] = np.where(df["Unstable"], df["Risk"]+" *", df["Risk"])

st.subheader("Recent risk")
st.dataframe(df[["date","place","mag","P","Risk"]])

last_I = df["I"].iloc[-1]
future = []
for i in range(1,4):
    d = (today + timedelta(days=i)).isoformat()
    P_fut = 1 / (1 + math.exp(-(last_I + intercept)))
    P_fut = max(min(P_fut, 0.99), 0.01)
    risk = "Low" if P_fut<0.25 else "Moderate" if P_fut<0.5 else "Elevated" if P_fut<0.75 else "Critical"
    future.append({"date":d,"P":P_fut,"Risk":risk})
st.subheader("Forward risk")
st.dataframe(pd.DataFrame(future))
