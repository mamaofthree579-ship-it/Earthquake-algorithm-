import streamlit as st
import requests, pandas as pd, numpy as np, math, json
from datetime import date, timedelta, datetime
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

st.title("Full‑Feature Risk Model")

# sidebar
st.sidebar.header("Params")
D = st.sidebar.slider("Diffusion D", 0.1, 1.0, 0.5, 0.1)
lam = st.sidebar.slider("Damping λ", 0.1, 1.0, 0.3, 0.1)
kappa = st.sidebar.slider("Nonlinear κ", 0.01, 0.05, 0.02, 0.01)

# user upload
upload = st.sidebar.file_uploader("Upload stress CSV", type="csv")
if upload:
    user_df = pd.read_csv(upload)
else:
    user_df = None

# fetch functions
@st.cache_data(ttl=600)
def fetch_eq(days):
    r = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={"format":"geojson",
                "starttime":(date.today()-timedelta(days=days)).isoformat(),
                "endtime":date.today().isoformat()},
        timeout=15
    )
    data = r.json()
    rows=[]
    for f in data.get("features",[]):
        p,g=f["properties"],f["geometry"]["coordinates"]
        rows.append({"date":datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
                     "place":p["place"],"mag":p["mag"] or 0,"lon":g[0],"lat":g[1]})
    return pd.DataFrame(rows)

df_recent = fetch_eq(7)
df_hist = fetch_eq(365)

# map
st.map(df_recent.rename(columns={"lat":"latitude","lon":"longitude"}))

choice = st.selectbox("Location", df_recent["place"].unique())
event = df_recent[df_recent["place"]==choice].iloc[0]
lat0, lon0 = np.radians(event.lat), np.radians(event.lon)
chi = np.cos(lat0)*np.sin(lon0)

# nearest station (stub: real call)
stations = requests.get("https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json", timeout=10).json()["stations"]
# pick first for demo
station_id = stations[0]["id"]
tide_url = f"https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&format=json&units=metric&time_zone=lst_ldt&station={station_id}"
tide_vals = [float(x["v"]) for x in requests.get(tide_url, timeout=10).json().get("predictions",[])][:len(df_recent)]

enso_url = "https://psl.noaa.gov/enso/data/nino34.data"
try:
    txt = requests.get(enso_url, timeout=10).text
    nums = [float(x) for x in txt.replace('\n',' ').split() if x.replace('.','',1).replace('-','',1).isdigit()]
    enso_val = nums[-1] if nums else 0.0
except:
    enso_val = 0.0

# ensemble solver
def run_ensemble(df):
    Ps=[]
    for _ in range(3):
        sigma=np.random.normal(0,0.01,N)
        sigs=[]
        for n in range(len(df)):
            S=math.sin(0.01*n); G=math.cos(0.008*n); V=event.mag
            O=chi*(tide_vals[n] if n<len(tide_vals) else 0 + enso_val)
            forcing=alpha*S+beta*G+gamma*V+delta*O+kappa*sigma**3+noise_amp*np.random.randn(N)
            sigma=spsolve(A, sigma+dt*(-lam*sigma+forcing))
            sigs.append(sigma.copy())
        I=np.array(sigs).mean(axis=1)
        Ps.append(1/(1+np.exp(-I)).clip(0.01,0.99))
    return np.mean(Ps,axis=0), np.std(Ps,axis=0)

alpha,beta,gamma,delta=0.1,0.05,0.2,0.08
noise_amp,dx,dt,N=0.05,1.0,0.01,200
main=np.ones(N)+2*dt*D/(dx**2)
off=-dt*D/(dx**2)*np.ones(N-1)
A=diags([off,main,off],[-1,0,1]).toarray()

df_recent["P_mean"], df_recent["P_std"] = run_ensemble(df_recent)
df_recent["Risk"]=df_recent["P_mean"].apply(lambda p:"Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

st.subheader("Recent risk")
st.dataframe(df_recent[["date","place","mag","P_mean","P_std","Risk"]])

# validation
if not df_hist.empty:
    df_hist["P_mean"],_ = run_ensemble(df_hist)
    corr = np.corrcoef(df_hist["mag"], df_hist["P_mean"])[0,1]
    st.caption(f"Historical mag‑P correlation: {corr:.2f}")

# export
csv = df_recent.to_csv(index=False)
st.download_button("Download CSV", csv, "risk.csv", "text/csv")
