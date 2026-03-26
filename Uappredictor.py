import streamlit as st
import datetime
import requests
import pandas as pd
import io
import math

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3

# --- Haversine Distance Function ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in kilometers
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Data Fetching Functions ---

@st.cache_data
def fetch_full_nuforc_dataset():
    """
    Downloads and caches the entire NUFORC dataset as a pandas DataFrame.
    This is the most robust method.
    """
    url = "http://www.nuforc.org/webreports/master_cep.csv"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        # The CSV has some formatting issues, so we need to clean it
        # It has a header and footer that need to be skipped.
        lines = response.text.splitlines()
        csv_io = io.StringIO('\n'.join(lines[1:-1])) # Skip first and last line
        df = pd.read_csv(csv_io)
        df.columns = df.columns.str.strip()
        # Clean up date and location data
        df['Event Date'] = pd.to_datetime(df['Date / Time'].str.split(' ').str[0], errors='coerce')
        df.dropna(subset=['Event Date', 'city', 'state'], inplace=True)
        # To improve geocoding, we combine city and state for a 'location' string
        df['location'] = df['city'].str.strip() + ", " + df['state'].str.strip()
        return df
    except Exception as e:
        st.error(f"Fatal Error: Could not download the master NUFORC database. {e}")
        return None

# --- Cache for Geocoding to avoid repeated API calls ---
@st.cache_data
def get_coords_for_city(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/2.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        return None

def fetch_local_earthquakes(stimulus_date, lat, lon, radius_km):
    start_time = stimulus_date.strftime("%Y-%m-%d") + "T00:00:00"
    end_time = (stimulus_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d") + "T23:59:59"
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}"
        f"&latitude={lat}&longitude={lon}&maxradiuskm={radius_km}&minmagnitude=4.0"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data['metadata']['count'] > 0:
            return data['features']
    except Exception:
        return []
    return []

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Correlation Engine", layout="wide")
st.title("Guardian Activity Correlation Engine")
st.markdown("This tool analyzes the **complete NUFORC database** to find correlations between UAP sightings and seismic activity.")

# --- Load the master dataset ---
nuforc_df = fetch_full_nuforc_dataset()

if nuforc_df is not None:
    st.success(f"Successfully loaded {len(nuforc_df):,} sightings from the master database.")

    st.sidebar.header("Analysis Parameters")
    search_radius_km = st.sidebar.slider("Search Radius (km)", 100, 1000, 300, 50)

    # Let user select a date range to analyze
    min_date = nuforc_df['Event Date'].min().date()
    max_date = nuforc_df['Event Date'].max().date()

    selected_date = st.sidebar.date_input("Select a start date for analysis", max_date - datetime.timedelta(days=30), min_value=min_date, max_value=max_date)

    # Filter the dataframe to a manageable chunk for display
    analysis_df = nuforc_df[nuforc_df['Event Date'].dt.date >= selected_date].sort_values('Event Date', ascending=False)

    if analysis_df.empty:
        st.warning("No sightings found for the selected date range.")
    else:
        st.info(f"Analyzing {len(analysis_df)} sightings since {selected_date.strftime('%Y-%m-%d')}...")

        for index, row in analysis_df.iterrows():
            sighting_date = row['Event Date']
            stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
            location_str = row['location']

            st.write("---")
            st.subheader(f"Sighting: {location_str} on {sighting_date.strftime('%Y-%m-%d')}")
            st.caption(f"Summary: {row['Summary']}")

            with st.spinner(f"Analyzing geological data for {location_str}..."):
                sighting_coords = get_coords_for_city(location_str)
                if sighting_coords:
                    earthquakes = fetch_local_earthquakes(stimulus_date, sighting_coords[0], sighting_coords[1], search_radius_km)

                    if earthquakes:
                        st.warning(f"**CORRELATION FOUND:** Found **{len(earthquakes)}** M4.0+ earthquakes within the search radius.")
                        for quake in earthquakes:
                            quake_mag = quake['properties']['mag']
                            quake_coords = (quake['geometry']['coordinates'][1], quake['geometry']['coordinates'][0])
                            distance = calculate_haversine_distance(sighting_coords[0], sighting_coords[1], quake_coords[0], quake_coords[1])
                            st.markdown(f"- **Mag {quake_mag:.1f}** earthquake **{distance:.0f} km away**.")
                    else:
                        st.success(f"**No Correlation:** No significant local seismic activity found in the {search_radius_km}km radius during the 3-day window.")
                else:
                    st.error(f"Could not find coordinates for '{location_str}'. Skipping analysis.")
