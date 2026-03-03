import streamlit as st
import requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

st.title("Real‑Forcing Stochastic Risk Model")

# constants
D, lam, kappa = 0.5, 0.3, 0.02
alpha, beta, gamma, delta = 0.1, 0.05, 0.2, 0.08
noise_amp, dx, dt = 0.05, 1.0, 0.01
N = 200
main = np.ones(N) + 2*dt*D/(dx**2)
off = -dt*D/(dx**2) * np.ones(N-1)
A = diags([off, main, off], [-1,0,1]).toarray()

@st.cache_data(ttl=600)
def fetch_eq():
    r = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={"format":"geojson","starttime":(date.today()-timedelta(days=7)).isoformat(),"endtime":date.today().isoformat()},
        timeout=15
    )
    data = r.json()
    rows=[]
    for f in data.get("features",[]):
        p,g=f["properties"],f["geometry"]["coordinates"]
        rows.append({"date":datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
                     "place":p["place"],"mag":p["mag"] or 0,"lon":g[0],"lat":g[1]})
    return pd.DataFrame(rows)

df = fetch_eq()
if df.empty:
    st.write("No quakes")
    st.stop()

# location picker
choice = st.selectbox("Location", df["place"].unique())
event = df[df["place"]==choice].iloc[0]
lat0, lon0 = np.radians(event.lat), np.radians(event.lon)
chi = np.cos(lat0)*np.sin(lon0)

# real tide: pick a fixed station (Seattle 9447130) for demo; replace with nearest lookup if desired
tide_url = "https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&format=json&units=metric&time_zone=lst_ldt&station=9447130"
tide = requests.get(tide_url, timeout=10).json()
tide_vals = [float(x["v"]) for x in tide["predictions"]][:len(df)]
# ENSO: Niño‑3.4 index (latest value) from PSL
enso_url = "https://psl.noaa.gov/enso/data/nino34.data"
txt = requests.get(enso_url, timeout=10).text
# last numeric value in file
enso_val = float([s for s in txt.split() if s.replace('.','',1).replace('-','',1).isdigit()][-1])

# ENSO fetch with safe parsing
enso_url = "https://psl.noaa.gov/enso/data/nino34.data"
try:
    txt = requests.get(enso_url, timeout=10).text
    # extract all numbers, take the last one
    nums = [float(x) for x in txt.replace('\n',' ').split() if x.replace('.','',1).replace('-','',1).isdigit()]
    enso_val = nums[-1] if nums else 0.0
except Exception:
    enso_val = 0.0
    
sigma = np.random.normal(0,0.01,N)
sigmas=[]
for n in range(len(df)):
    S = math.sin(0.01*n)
    G = math.cos(0.008*n)
    V = event.mag
    O = chi * (delta * (tide_vals[n] if n<len(tide_vals) else 0) + delta*enso_val)
    forcing = (alpha*S + beta*G + gamma*V + O + kappa*sigma**3 + noise_amp*np.random.randn(N))
    rhs = sigma + dt*(-lam*sigma + forcing)
    sigma = spsolve(A, rhs)
    sigmas.append(sigma.copy())

I = np.array(sigmas).mean(axis=1)
df["I"]=I
df["P"]=1/(1+np.exp(-df["I"])).clip(0.01,0.99)
df["Risk"]=df["P"].apply(lambda p: "Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

st.subheader("Recent risk (real forcings)")
st.dataframe(df[["date","place","mag","P","Risk"]])
