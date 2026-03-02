import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from sklearn.linear_model import LogisticRegression

st.title("Nonlinear Diffusion‑Fracture Risk Model")

# ----- new constants -----
mu_v, kappa_v, eta_v = 0.5, 0.1, 0.05
D, rho, crit_k = 0.3, 0.2, 0.1
tau_T, tau_E = 0.05, 0.04 # loading coefficients
zeta = 0.01 # fracture nonlinearity
dx = 1.0
dt = 0.2 # satisfies dt <= dx²/(4D)

# ----- upload -----
uploaded = st.file_uploader("Upload past quakes CSV (date,mag,place)", type="csv")
if uploaded:
    df_hist = pd.read_csv(uploaded)
    df_hist.columns = df_hist.columns.str.lower().str.strip()
    if "mag" not in df_hist.columns or "date" not in df_hist.columns:
        st.warning("CSV needs date and mag")
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

# placeholder tidal and ENSO indices (real app would fetch)
tidal = np.sin(np.arange(7)*0.8) # synthetic
enso = np.cos(np.arange(7)*0.3)

frames = []
for idx, frame in enumerate((df_hist, df)):
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
    # oceanic loading (simple synthetic sensitivity)
    frame["L_o"] = 0.1 * (tau_T * tidal[idx%7] + tau_E * enso[idx%7])
    frame["W"] = 1 + 0.3 * (1 - frame["flare"])
    frame["C"] = 0.6 * frame["flare"]
    frames.append(frame)

if len(frames)==2:
    df_hist, df = frames
else:
    df = frames[0]

if not df_hist.empty:
    df_hist["target"] = (df_hist["mag"] >= 5).astype(int)
    X = df_hist[["S_t","C","W","P_v","L_o"]].fillna(0)
    y = df_hist["target"]
    model = LogisticRegression().fit(X, y)
    coef = model.coef_[0]
    intercept = model.intercept_[0]
else:
    coef = np.array([1.0, 0.4, 0.3, mu_v, 0.02])
    intercept = 0.0

# nonlinear update: I += dt*(D∇²I + F - rho I + zeta I³)
df["F_total"] = (coef[2]*df["W"]*df["S_t"] + coef[1]*df["C"] +
                 coef[3]*df["P_v"] + coef[4]*df["L_o"])
df["I"] = 0.0
for i in range(1, len(df)):
    lap = 0 # grid proxy → 0 for 1D list
    forcing = df["F_total"].iloc[i]
    I_prev = df["I"].iloc[i-1]
    dI = dt * (D*lap + forcing - rho*I_prev + zeta*(I_prev**3))
    df["I"].iloc[i] = I_prev + dI

df["P"] = 1 / (1 + np.exp(-(df["I"] + intercept)))
df["P"] = df["P"].clip(0.01, 0.99)
df["Risk"] = df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

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
