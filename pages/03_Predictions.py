import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.title("7‑Day Quake Predictions")

csv = Path("data/sample_quakes.csv")
if not csv.exists():
    st.warning("Build old data first")
    st.stop()

df = pd.read_csv(csv)
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce").fillna(0)
df["solar_flare_window"] = pd.to_numeric(df["solar_flare_window"], errors="coerce").fillna(0).astype(int)

# ---- model ----
base_rates = { 
    "Alaska":0.9, "California":0.6, "Chile":0.8, "Japan":0.8,
    "Indonesia":0.9, "Greece":0.5, "Turkey":0.7, "Mexico":0.6
}
w_region=0.30; w_flare=0.25; w_quant=0.25; w_day=0.10; w_bias=0.05
quant = df["magnitude"].rank(pct=True)
ref_day = df.index.min()
days = df.index - ref_day

def pin_row(r):
    key = next((k for k in base_rates if k.lower() in str(r["place"]).lower()), None)
    region_risk = base_rates.get(key,0.3)
    days_ago_norm = 1/(1+days[r.name])
    prob = (w_region*region_risk + w_flare*r["solar_flare_window"] +
            w_quant*quant[r.name] + w_day*days_ago_norm + w_bias*1.0)
    return min(prob,1.0)

df["elevated_risk_prob"] = df.apply(pin_row, axis=1)
df["predicted_magnitude_offset"] = np.tanh(df["elevated_risk_prob"]-0.5)*1.5
df["predicted_magnitude"] = (df["magnitude"]+df["predicted_magnitude_offset"]).clip(4.0,8.5)

# ---- top‑5 ----
top = df.nlargest(5,"elevated_risk_prob")[["date","place","magnitude","predicted_magnitude","elevated_risk_prob"]]
st.subheader("Top 5 elevated‑risk places (7‑day)")
st.dataframe(top)
