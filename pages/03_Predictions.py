import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

st.title("Stochastic Stress‑Field Risk Model")

# ----- PDE constants -----
D = 0.5
lam = 0.3
kappa = 0.02
alpha = 0.1
beta = 0.05
gamma = 0.2
delta = 0.08
noise_amp = 0.05
dx = 1.0
dt = 0.01
N = 200 # grid points

# build implicit diffusion matrix
main = np.ones(N) + 2*dt*D/(dx**2)
off = -dt*D/(dx**2) * np.ones(N-1)
A = diags([off, main, off], [-1,0,1]).toarray()

# ----- fetch recent quakes -----
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
        p = f["properties"]
        rows.append({
            "date": datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
            "mag": p["mag"] or 0
        })
    return pd.DataFrame(rows)

df = fetch(start_recent, end)
if df.empty:
    st.write("No recent quakes")
    st.stop()

# ----- simple forcing proxies -----
S = np.sin(0.01*np.arange(len(df))) # solar
G = np.cos(0.008*np.arange(len(df))) # geomagnetic
V = df["mag"].values # volcanic proxy
O = 0.5*np.cos(0.005*np.arange(len(df))) # ocean loading proxy

# ----- evolve sigma field -----
sigma = np.random.normal(0, 0.01, N)
sigmas = []
for n in range(len(df)):
    forcing = (alpha*S[n] + beta*G[n] + gamma*V[n] + delta*O[n] +
               kappa*sigma**3 + noise_amp*np.random.randn(N))
    rhs = sigma + dt*(-lam*sigma + forcing)
    sigma = spsolve(A, rhs)
    sigmas.append(sigma.copy())

sigmas = np.array(sigmas)
I = sigmas.mean(axis=1) # spatial average as instability index

df["I"] = I
df["P"] = 1 / (1 + np.exp(-df["I"]))
df["P"] = df["P"].clip(0.01, 0.99)
df["Risk"] = df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

st.subheader("Recent risk")
st.dataframe(df[["date","mag","P","Risk"]])

# forward forecast using last sigma
sigma_last = sigma
future = []
for i in range(1,4):
    d = (today + timedelta(days=i)).isoformat()
    # one step forward with mean forcings
    forcing = (alpha*np.sin(0.01*(len(df)+i)) + beta*np.cos(0.008*(len(df)+i)) +
               gamma*df["mag"].mean() + delta*0.5*np.cos(0.005*(len(df)+i)) +
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
