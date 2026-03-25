import streamlit as st
import datetime
import requests
import pandas as pd

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3
SEARCH_RADIUS_KM = 500 # Look for quakes within a 500km radius of the sighting

# --- Data Fetching Functions ---

def fetch_sighting_data():
    """ Fetches the latest UAP sightings from a public API. """
    # Using a public API that scrapes NUFORC data
    url = "https://nuforc.org/webreports/ndxpost.html"
    try:
        # We need to use pandas to scrape the HTML table directly
        tables = pd.read_html(url)
        df = tables[0]
        # Rename columns for easier use
        df.columns = ['Date / Time', 'City', 'State', 'Country', 'Shape', 'Duration', 'Summary', 'Posted', 'Images']
        # Convert date/time to a consistent format
        df['Event Date'] = pd.to_datetime(df['Date / Time'].str.split(' ').str[0], errors='coerce')
        # Drop rows where date conversion failed
        df.dropna(subset=['Event Date'], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Could not fetch sighting data from NUFORC: {e}")
        return pd.DataFrame()

def get_coords_for_city(city, state):
    """ Gets latitude and longitude for a city using a free geocoding API. """
    url = f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Predictor/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        # Silently fail, as some city names might be messy
        return None, None

def fetch_local_earthquakes(stimulus_date, lat, lon, radius_km):
    """ Fetches earthquakes near a specific location. """
    start_time = f"{stimulus_date}T00:00:00"
    # We'll check the full 3-day window
    end_time = (stimulus_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d") + "T23:59:59"
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}"
        f"&latitude={lat}&longitude={lon}&maxradiuskm={radius_km}&minmagnitude=4.0" # Lowered mag for local sensitivity
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

st.info("Fetching the latest UAP sighting reports from the National UFO Reporting Center (NUFORC)...")

sighting_df = fetch_sighting_data()

if not sighting_df.empty:
    st.success(f"Successfully fetched {len(sighting_df)} recent sighting reports.")

    # We only have resources to process the last N sightings
    sightings_to_process = st.slider("Number of recent sightings to analyze:", 5, 50, 10)

    for index, row in sighting_df.head(sightings_to_process).iterrows():
        sighting_date = row['Event Date']
        stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
        city, state = row['City'], row['State']

        st.write("---")
        st.subheader(f"Sighting: {city}, {state} on {sighting_date.strftime('%Y-%m-%d')}")
        st.caption(f"Summary: {row['Summary']}")

        with st.spinner(f"Analyzing geological data for {city}, {state}..."):
            lat, lon = get_coords_for_city(city, state)
            if lat and lon:
                quake_count, max_mag = fetch_local_earthquakes(stimulus_date, lat, lon, SEARCH_RADIUS_KM)

                if quake_count > 0:
                    st.warning(f"**CORRELATION FOUND:** Found **{quake_count}** M4.0+ earthquakes within {SEARCH_RADIUS_KM}km in the 3 days prior. Max Magnitude: **{max_mag:.2f}**.")
                else:
                    st.success(f"**No Correlation:** No significant local seismic activity found in the 3 days prior to the sighting.")
            else:
                st.error(f"Could not find geographic coordinates for '{city}, {state}'. Skipping analysis.")

else:
    st.error("Could not retrieve sighting data. The source may be down or the format may have changed.")
