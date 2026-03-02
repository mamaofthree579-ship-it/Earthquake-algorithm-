import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

st.title("Geospatial Stochastic Risk Model")

# ----- constants -----
D, lam, kappa = 0.5, 0.3, 0.02
alpha, beta, gamma, delta = 0.1, 0.05, 0.2, 0.08
noise_amp, dx, dt = 0.05, 1.0, 0.01
N = 200
main = np.ones(N) + 2*dt*D/(dx**2)
off = -dt*D/(dx**2) * np.ones(N-1)
A = diags([off, main, off], [-1,0,1]).toarray()

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
    except:
        return pd.DataFrame()
    rows = []
    for f in data.get("features", []):
        p, g = f["properties"], f["geometry"]["coordinates"]
        rows.append({
            "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
            "place": p["place"],
            "mag": p["mag"] or 0,
            "lon": g[0],
            "lat": g[1]
        })
    return pd.DataFrame(rows)

df = fetch(start_recent, end)
if df.empty:
    st.write("No recent quakes")
    st.stop()

places = df["place"].unique().tolist()
choice = st.selectbox("Choose event location", places)
event = df[df["place"] == choice].iloc[0]
lat0, lon0 = np.radians(event.lat), np.radians(event.lon)
chi = np.cos(lat0) * np.sin(lon0) # spatial sensitivity
st.caption(f"Lat {event.lat:.2f}, Lon {event.lon:.2f}")

# ----- PDE evolution -----
sigma = np.random.normal(0, 0.01, N)
sigmas = []
for n in range(len(df)):
    S = math.sin(0.01*n)
    G = math.cos(0.008*n)
    V = event.mag
    O = chi * (0.5*math.cos(0.005*n)) # lat/lon‑weighted loading
    forcing = (alpha*S + beta*G + gamma*V + delta*O +
               kappa*sigma**3 + noise_amp*np.random.randn(N))
    rhs = sigma + dt*(-lam*sigma + forcing)
    sigma = spsolve(A, rhs)
    sigmas.append(sigma.copy())

I = np.array(sigmas).mean(axis=1)
df["I"] = I
df["P"] = 1 / (1 + np.exp(-df["I"]))
df["P"] = df["P"].clip(0.01, 0.99)
df["Risk"] = df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

st.subheader("Recent risk (coords‑aware)")
st.dataframe(df[["date","place","mag","P","Risk"]])

# forward forecast
sigma_last = sigma
future = []
for i in range(1,4):
    d = (today + timedelta(days=i)).isoformat()
    S = math.sin(0.01*(len(df)+i))
    G = math.cos(0.008*(len(df)+i))
    O = chi * (0.5*math.cos(0.005*(len(df)+i)))
    forcing = (alpha*S + beta*G + gamma*event.mag + delta*O +
               kappa*sigma_last**3 + noise_amp*np.random.randn(N))
    rhs = sigma_last + dt*(-lam*sigma_last + forcing)
    sigma_last = spsolve(A, rhs)
    I_fut = sigma_last.mean()
    P_fut = 1 / (1 + math.exp(-I_fut))
    P_fut = max(min(P_fut, 0.99), 0.01)
    risk = "Low" if P_fut<0.25 else "Moderate" if P_fut<0.5 else "Elevated" if P_fut<0.75 else "Critical"
    future.append({"date":d,"P":P_fut,"Risk":risk})

st.subheader("Forward risk")
st.dataframe(pd.DataFrame(future))
