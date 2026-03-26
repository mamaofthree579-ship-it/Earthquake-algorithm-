import streamlit as st
import datetime
import requests
import pandas as pd

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3
SEARCH_RADIUS_KM = 500 # Look for quakes within a 500km radius of the sighting

# --- Data Fetching Functions ---

def fetch_sighting_data():
    """ Fetches the latest UAP sightings from a public JSON API. """
    # This API provides NUFORC data in a clean JSON format
    url = "https://www.ufo-api.com/api/reports/newest"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        # Convert date/time to a consistent format
        df['Event Date'] = pd.to_datetime(df['date_time'], errors='coerce')
        # Drop rows where date conversion failed
        df.dropna(subset=['Event Date'], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Could not fetch sighting data from the JSON API: {e}")
        return pd.DataFrame()

def get_coords_for_city(city, state):
    """ Gets latitude and longitude for a city using a free geocoding API. """
    # Handle cases where state might be missing or is not US
    query = f"{city}, {state}" if state else city
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        return None, None

def fetch_local_earthquakes(stimulus_date, lat, lon, radius_km):
    """ Fetches earthquakes near a specific location. """
    start_time = f"{stimulus_date}T00:00:00"
    end_time = (stimulus_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d") + "T23:59:59"
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}"
        f"&latitude={lat}&longitude={lon}&maxradiuskm={radius_km}&minmagnitude=4.0"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        count = data['metadata']['count']
        max_mag = 0
        if count > 0:
            largest_quake = max(data['features'], key=lambda x: x['properties']['mag'])
            max_mag = largest_quake['properties']['mag']
        return count, max_mag
    except Exception:
        return 0, 0

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Correlation Engine", layout="wide")
st.title("Guardian Activity Correlation Engine")
st.markdown("This tool automatically correlates live UAP sighting data with local geological stress events.")

st.info("Fetching the latest UAP sighting reports from a public JSON API...")

sighting_df = fetch_sighting_data()

if not sighting_df.empty:
    st.success(f"Successfully fetched {len(sighting_df)} recent sighting reports.")

    sightings_to_process = st.slider("Number of recent sightings to analyze:", 5, 50, 10)

    for index, row in sighting_df.head(sightings_to_process).iterrows():
        sighting_date = row['Event Date']
        stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
        city, state = row['city'], row.get('state', '') # Use.get for safety

        st.write("---")
        st.subheader(f"Sighting: {city}, {state} on {sighting_date.strftime('%Y-%m-%d')}")
        st.caption(f"Summary: {row['summary']}")

        with st.spinner(f"Analyzing geological data for {city}, {state}..."):
            lat, lon = get_coords_for_city(city, state)
            if lat and lon:
                quake_count, max_mag = fetch_local_earthquakes(stimulus_date, lat, lon, SEARCH_RADIUS_KM)

                if quake_count > 0:
                    st.warning(f"**CORRELATION FOUND:** Found **{quake_count}** M4.0+ earthquakes within {SEARCH_RADIUS_KM}km in the 3 days prior. Max Magnitude: **{max_mag:.2f}**.")
                else:
                    st.success(f"**No Correlation:** No significant local seismic activity found in the 3 days prior to the sighting.")
            else:
                st.error(f"Could not find geographic coordinates for '{city}, {state}'. It may be a non-specific location. Skipping analysis.")

else:
    st.error("Could not retrieve sighting data. The source API may be temporarily down.")
