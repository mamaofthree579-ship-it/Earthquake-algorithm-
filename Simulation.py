import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np
import pywt

st.set_page_config(page_title="Geo Signal Simulator", layout="wide")
st.title("Terrestrial Signal Simulator (Starter)")

# 1) Ingest USGS daily quakes
@st.cache_data(ttl=900)
def load_usgs():
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson"
        f"?starttime={week_ago.date()}&endtime={today.date()}&minmagnitude=4"
    )
    r = requests.get(url)
    data = r.json()
    rows = [
        {"time": f["properties"]["time"], "mag": f["properties"]["mag"],
         "place": f["properties"]["place"]}
        for f in data["features"]
    ]
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

df = load_usgs()
st.subheader("Recent M4+ quakes")
st.map(df.rename(columns={"latitude": "lat", "longitude": "lon"}).fillna(0))

# 2) Wavelet transform of magnitude series
mag_series = df.sort_values("time")["mag"].fillna(0).values
if len(mag_series) > 32:
    scales = np.arange(1, 64)
    coeff, _ = pywt.cwt(mag_series, scales, "morl")
    st.subheader("Wavelet scalogram (Morlet)")
    st.line_chart(np.abs(coeff).mean(axis=1))

# 3) Toy risk gauge
recent = df[df["time"] > datetime.utcnow() - timedelta(hours=24)]
score = min(1.0, recent["mag"].sum() / 30)
level = "Low" if score < 0.3 else "Moderate" if score < 0.6 else "Elevated"
st.metric("24h seismic risk", level)
