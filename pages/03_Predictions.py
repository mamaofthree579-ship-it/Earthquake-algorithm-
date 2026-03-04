import streamlit as st, requests, pandas as pd, numpy as np, math
from datetime import date, timedelta, datetime
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve
from scipy.stats import spearmanr

st.title("Earthquake Risk – PDE with Real Forcings")
st.markdown("**Model:** ∂σ/∂t = D∇²σ – λσ + αS + βG + γV + δO + κσ³ + η")

st.sidebar.header("Params")
D = st.sidebar.slider("Diffusion D", 0.1,1.0,0.5,0.1)
lam = st.sidebar.slider("Damping λ",0.1,1.0,0.3,0.1)
kappa = st.sidebar.slider("Nonlinear κ",0.01,0.05,0.02,0.01)

@st.cache_data(ttl=600)
def fetch_eq(days):
    try:
        r = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            params={"format":"geojson",
                    "starttime":(date.today()-timedelta(days=days)).isoformat(),
                    "endtime":date.today().isoformat()},
            timeout=10)
        r.raise_for_status()
        data=r.json()
    except Exception as e:
        st.warning(f"USGS fetch failed: {e}")
        return pd.DataFrame()
    rows=[]
    for f in data.get("features",[]):
        p,g=f["properties"],f["geometry"]["coordinates"]
        rows.append({"date":datetime.utcfromtimestamp(p["time"]/1000).strftime("%Y-%m-%d"),
                     "place":p["place"],"mag":p["mag"] or 0,"lon":g[0],"lat":g[1]})
    return pd.DataFrame(rows)

df_recent=fetch_eq(7)
if df_recent.empty:
    st.stop()
df_hist=fetch_eq(30)

st.map(df_recent.rename(columns={"lat":"latitude","lon":"longitude"}))
choice=st.selectbox("Location",df_recent["place"].unique())
event=df_recent[df_recent["place"]==choice].iloc[0]
lat0,lon0=np.radians(event.lat),np.radians(event.lon)
chi=math.cos(lat0)*math.sin(lon0)

stations=requests.get("https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json",timeout=10).json()["stations"]
def havers(lat1,lon1,lat2,lon2):
    R=6371;phi1,phi2=math.radians(lat1),math.radians(lat2)
    dphi=math.radians(lat2-lat1);dlambda=math.radians(lon2-lon1)
    a=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(a))
dists=[havers(event.lat,event.lon,s["lat"],s["lng"]) for s in stations]
station_id=stations[int(np.argmin(dists))]["id"]

tide_url=f"https://tidesandcurrents.noaa.gov/api/datagetter?date=today&product=predictions&datum=mllw&format=json&units=metric&time_zone=lst_ldt&station={station_id}"
try:
    tide_vals=[float(x["v"]) for x in requests.get(tide_url,timeout=10).json().get("predictions",[])]
except Exception:
    st.warning("Tide fetch failed, using zeros")
    tide_vals=[0.0]*len(df_recent)

enso_val=0.0
for url in ("https://psl.noaa.gov/enso/data/nino34.data",
            "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"):
    try:
        txt=requests.get(url,timeout=10).text
        nums=[float(x) for x in txt.replace("\n"," ").split() if x.replace(".","",1).replace("-","",1).isdigit()]
        if nums:
            enso_val=nums[-1]
            break
    except Exception:
        continue
if enso_val==0.0:
    st.warning("ENSO fetch failed, using 0")

alpha,beta,gamma,delta=0.1,0.05,0.2,0.08
noise_amp,dx,dt,N=0.05,1.0,0.01,200
main=np.ones(N)+2*dt*D/(dx**2)
off=-dt*D/(dx**2)*np.ones(N-1)
A=diags([off,main,off],[-1,0,1]).toarray()

File "/mount/src/earthquake-algorithm-/pages/03_Predictions.py", line 101, in <module>
    df_recent["P_mean"],df_recent["P_std"]=run_ens(df_recent)
                                           ~~~~~~~^^^^^^^^^^^
File "/mount/src/earthquake-algorithm-/pages/03_Predictions.py", line 92, in run_ens
    V=math.log1p(mag_val) + np.random.normal(0,0.001)
      ~~~~~~~~~~^^^^^^^^^

df_recent["P_mean"],df_recent["P_std"]=run_ens(df_recent)
df_recent["Risk"]=df_recent["P_mean"].apply(lambda p:"Low" if p<0.25 else "Moderate" if p<0.5 else "Elevated" if p<0.75 else "Critical")

st.subheader("Recent risk")
st.dataframe(df_recent[["date","place","mag","P_mean","P_std","Risk"]])

if not df_hist.empty:
    df_hist["P_mean"],_=run_ens(df_hist)
    rho,_=spearmanr(df_hist["mag"],df_hist["P_mean"] )
    st.caption(f"Historical Spearman rank correlation: {rho:.2f}")

csv=df_recent.to_csv(index=False)
st.download_button("Download CSV",csv,"risk.csv","text/csv")
