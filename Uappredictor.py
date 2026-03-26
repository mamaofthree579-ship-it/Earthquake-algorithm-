import streamlit as st
import datetime
import requests
import pandas as pd
import io
import math

# --- Haversine Distance Function ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in kilometers
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Data Loading Function ---
@st.cache_data
def load_dataset_from_url(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))

        # --- Data Cleaning ---
        df.columns = df.columns.str.strip()
        df['Event Date'] = pd.to_datetime(df['reported_date_time'], errors='coerce')
        df.dropna(subset=['Event Date', 'city', 'state'], inplace=True)
        df['location'] = df['city'].str.strip() + ", " + df['state'].str.strip()
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to download data from the URL: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred while processing the data: {e}")
        return None

# --- Geocoding and Earthquake Functions ---
@st.cache_data
def get_coords_for_city(location):
    # Function definition remains the same
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/4.0'} # Final version
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        return None

def fetch_local_earthquakes(stimulus_date, lat, lon, radius_km, lag_days):
    # Function definition remains the same
    start_time = (sighting_date - datetime.timedelta(days=lag_days)).strftime("%Y-%m-%d")
    end_time = sighting_date.strftime("%Y-%m-%d")
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}"
        f"&latitude={lat}&longitude={lon}&maxradiuskm={radius_km}&minmagnitude=4.0"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json().get('features', [])
    except Exception:
        return []

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Correlation Engine", layout="wide")
st.title("Guardian Activity Correlation Engine")

st.info("Paste the URL to the raw NUFORC CSV file below to begin analysis.")
data_url = st.text_input("Dataset URL:", "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2023/2023-06-20/ufo_sightings.csv")

if st.button("Analyze Data") and data_url:
    nuforc_df = load_dataset_from_url(data_url)

    if nuforc_df is not None:
        st.success(f"Successfully loaded {len(nuforc_df):,} sightings from the URL.")

        st.sidebar.header("Analysis Parameters")
        prediction_lag_days = st.sidebar.slider("Prediction Lag (Days Before Sighting)", 1, 7, 3)
        search_radius_km = st.sidebar.slider("Search Radius (km)", 100, 1000, 300, 50)

        analysis_df = nuforc_df.sort_values('Event Date', ascending=False)

        for index, row in analysis_df.head(200).iterrows(): # Limit to first 200 for performance
            sighting_date = row['Event Date']
            location_str = row['location']

            st.write("---")
            st.subheader(f"Sighting: {location_str} on {sighting_date.strftime('%Y-%m-%d')}")
            st.caption(f"Summary: {row['summary']}")

            with st.spinner(f"Analyzing geological data for {location_str}..."):
                sighting_coords = get_coords_for_city(location_str)
                if sighting_coords:
                    earthquakes = fetch_local_earthquakes(sighting_date, sighting_coords[0], sighting_coords[1], search_radius_km, prediction_lag_days)
                    if earthquakes:
                        st.warning(f"**CORRELATION FOUND:** Found **{len(earthquakes)}** M4.0+ earthquakes within the search window.")
                        for quake in earthquakes:
                            quake_mag = quake['properties']['mag']
                            quake_coords = (quake['geometry']['coordinates'][1], quake['geometry']['coordinates'][0])
                            distance = calculate_haversine_distance(sighting_coords[0], sighting_coords[1], quake_coords[0], quake_coords[1])
                            st.markdown(f"- **Mag {quake_mag:.1f}** earthquake **{distance:.0f} km away**.")
                    else:
                        st.success(f"**No Correlation:** No significant local seismic activity found within the parameters.")
                else:
                    st.error(f"Could not find coordinates for '{location_str}'.")
