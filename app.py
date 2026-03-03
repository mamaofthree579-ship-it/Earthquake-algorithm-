import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(layout="wide")
st.title("🌍 IHRAS Research Dashboard")

# -------------------------------------------------
# DATA INGESTION LAYER
# -------------------------------------------------

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_usgs_data():

    try:
        response = requests.get(USGS_URL, timeout=10)
        response.raise_for_status()

        data = response.json()

        records = []

        for feature in data.get("features", []):

            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            if not coords or props.get("mag") is None:
                continue

            records.append({
                "longitude": coords[0],
                "latitude": coords[1],
                "depth": coords[2] if len(coords) > 2 else np.nan,
                "magnitude": props.get("mag"),
                "place": props.get("place", "")
            })

        df = pd.DataFrame(records)

        # Schema normalization
        required_cols = ["longitude","latitude","magnitude","place"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = np.nan

        return df

    except Exception as e:
        st.error(f"Data ingestion error: {e}")
        return pd.DataFrame(columns=[
            "longitude","latitude","magnitude","place"
        ])

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = fetch_usgs_data()

# Safe cleaning pipeline
if df is not None and not df.empty:

    df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")

    df = df.dropna(subset=["longitude","latitude","magnitude"])

    df = df[df["magnitude"] > 0]

    # Plotly safety clamp
    df["marker_size"] = np.clip(df["magnitude"] * 2, 2, 20)

else:
    df = pd.DataFrame(columns=[
        "longitude","latitude","magnitude","place","marker_size"
    ])

# -------------------------------------------------
# VISUALIZATION LAYER
# -------------------------------------------------

st.header("🌎 Global Earthquake Activity Map")

fig = go.Figure()

if not df.empty:

    fig.add_trace(go.Scattergeo(
        lon=df["longitude"].tolist(),
        lat=df["latitude"].tolist(),
        text=df["place"].fillna("").tolist(),
        mode="markers",
        marker=dict(
            size=df["marker_size"].tolist(),
            color=df["magnitude"].tolist(),
            colorscale="Viridis",
            showscale=True
        )
    ))

fig.update_geos(
    projection_type="natural earth",
    showcountries=True,
    showland=True
)

fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# SYSTEM STABILITY METRIC (Research Proxy Only)
# -------------------------------------------------

st.header("📊 System Stability Indicator")

if not df.empty:
    stability_index = 1 / (1 + np.var(df["magnitude"]))
else:
    stability_index = 1.0

st.metric(
    "Stability Index",
    f"{stability_index:.4f}"
)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("---")
st.caption("IHRAS Research Prototype — Not a prediction system")
