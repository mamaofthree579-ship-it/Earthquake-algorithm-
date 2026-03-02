import streamlit as st
import plotly.express as px
import numpy as np
from ingestion.usgs import fetch_earthquakes
from ingestion.noaa import fetch_enso_index
from ingestion.solar import fetch_kp_index
from utils.harmonics import celestial_forcing

st.header("Live Earthquake Map")

if df.empty:
    st.warning("No earthquake data available.")
else:
    # ---------- HARD TYPE ENFORCEMENT ----------
    df = df.copy()

    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["mag", "lat", "lon"])

    df = df[df["mag"] > 0]
    df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]

    # ---------- SAFE SIZE SCALING ----------
    df["size_scaled"] = np.clip(df["mag"], 0.1, 10)

    if df.empty:
        st.warning("No valid earthquake data after cleaning.")
    else:
        fig = px.scatter_geo(
            df,
            lat="lat",
            lon="lon",
            size="size_scaled",
            hover_name="place",
            projection="natural earth",
            size_max=12
        )

        fig.update_layout(
            geo=dict(
                showland=True,
                landcolor="rgb(240,240,240)",
                showcountries=True
            )
        )

        st.plotly_chart(fig, use_container_width=True)
# -------------------------
# Earthquake Map
# -------------------------

st.header("Live Earthquake Map")

if df.empty:
    st.warning("No earthquake data available.")
else:
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        size="mag",
        hover_name="place",
        color="mag",
        projection="natural earth",
        size_max=12
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Harmonic Stress Forecast
# -------------------------

st.header("Monte Carlo Stress Projection")

grid = np.random.rand(90,180)
fig2 = px.imshow(grid, origin="lower")
st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Risk Index Calculation
# -------------------------

stress_mean = np.mean(grid)
risk = (stress_mean + abs(celestial) + abs(enso) + kp) / 3

if risk < 0.5:
    status = "Low"
elif risk < 1.0:
    status = "Moderate"
elif risk < 2.0:
    status = "Elevated"
else:
    status = "Critical"

st.subheader(f"🌡 Event Risk Index: {status}")
