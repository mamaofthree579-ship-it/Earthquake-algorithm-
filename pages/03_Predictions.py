import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from sklearn.linear_model import LogisticRegression

st.title("Trained Harmonic Stress Risk Model")

# ----- optional spreadsheet -----
uploaded = st.file_uploader("Upload past quakes CSV (columns: date, place, mag)", type="csv")
if uploaded:
    df_upload = pd.read_csv(uploaded, parse_dates=["date"])
    df_upload["date"] = df_upload["date"].dt.strftime("%Y-%m-%d")
else:
    df_upload = pd.DataFrame()

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

hist_frames = []
for i in range(3):
    chunk_end = (today - timedelta(days=i*30+7)).isoformat()
    chunk_start = (today - timedelta(days=(i+1)*30+7)).isoformat()
    hist_frames.append(fetch(chunk_start, chunk_end))
df_hist = pd.concat(hist_frames, ignore_index=True) if hist_frames else pd.DataFrame()
df_hist = pd.concat([df_hist, df_upload], ignore_index=True) # <-- merge upload

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
        lambda x: np.sum(x*np.sin(np.arange(len(x)))), raw=False
    )
    frame["W"] = 1 + 0.3 * (1 - frame["flare"])
    frame["C"] = 0.6 * frame["flare"]

if not df_hist.empty:
    df_hist["target"] = (df_hist["mag"] >= 5).astype(int)
    X = df_hist[["S_t","C","W"]].fillna(0)
    y = df_hist["target"]
    model = LogisticRegression().fit(X, y)
    coef_S, coef_C, coef_W = model.coef_[0]
    intercept = model.intercept_[0]
else:
    coef_S, coef_C, coef_W, intercept = 1.0, 0.4, 0.3, 0.0

df["I"] = coef_W * df["W"] * df["S_t"] + coef_C * df["C"]
df["P"] = 1 / (1 + np.exp(-(df["I"] + intercept)))
df["Risk"] = df["P"].apply(
    lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical"
)

st.subheader("Recent risk")
st.dataframe(df[["date","place","mag","P","Risk"]])

last_I = df["I"].iloc[-1]
future = []
for i in range(1,4):
    d = (today + timedelta(days=i)).isoformat()
    P_fut = 1 / (1 + math.exp(-(last_I + intercept)))
    P_fut = max(min(P_fut, 0.99), 0.01)
    future.append({"date":d,"P":P_fut,"Risk": "Low" if P_fut<0.25 else "Moderate" if P_fut<0.5 else "Elevated" if P_fut<0.75 else "Critical"})
st.subheader("Forward risk")
st.dataframe(pd.DataFrame(future))

st.title("Extended Harmonic‑Diffusion Risk Model")

# ----- constants for new physics -----
mu_v = 0.5 # volcanic coupling
kappa_v = 0.1 # chamber compressibility
eta_v = 0.05 # volcanic damping
D = 0.3 # stress diffusion coeff
rho = 0.2 # relaxation rate
crit_k = 0.1 # representative wavenumber (long‑wavelength)

# ----- file upload (optional) -----
uploaded = st.file_uploader("Upload past quakes CSV (date,mag,place)", type="csv")
if uploaded:
    df_hist = pd.read_csv(uploaded, parse_dates=["date"])
    df_hist["date"] = df_hist["date"].dt.strftime("%Y-%m-%d")
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

# cosmic flare flag
flares = requests.get(
    "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    timeout=15
).json()
flare_days = {item["begin_time"][:10] for item in flares}

# ----- build feature frames -----
frames = []
for frame in (df_hist, df):
    if frame.empty:
        continue
    frame = frame.copy()
    frame["flare"] = frame["date"].isin(flare_days).astype(int)
    frame["S_t"] = frame["mag"].rolling(3, min_periods=1).apply(
        lambda x: np.sum(x*np.sin(np.arange(len(x)))), raw=False
    )
    # volcanic pressure (simple Euler step, Q_in‑Q_out ~ flare*mag)
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

# train logistic model on extended features
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

# instability index with diffusion smoothing
df["I_raw"] = (coef[3]*df["P_v"] + coef[2]*df["W"]*df["S_t"] + coef[1]*df["C"])
df["I"] = df["I_raw"].rolling(3, min_periods=1).mean() # proxy for D∇²I - ρI
df["I"] = df["I"] - rho*df["I_raw"] # relaxation

# forcing vs critical
F_total = df["W"]*df["S_t"] + df["C"] + mu_v*df["P_v"]
F_crit = rho + D*(crit_k**2)
df["Unstable"] = F_total > F_crit

# probability
df["P"] = 1 / (1 + np.exp(-(df["I"] + intercept)))
df["P"] = df["P"].clip(0.01, 0.99)
df["Risk"] = df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")
df["Risk"] = np.where(df["Unstable"], df["Risk"] + " *", df["Risk"]) # mark unstable

st.subheader("Recent risk")
st.dataframe(df[["date","place","mag","P","Risk"]])

# forward forecast (reuse last I)
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
