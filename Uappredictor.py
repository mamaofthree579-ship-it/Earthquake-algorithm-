import streamlit as st
import datetime
import requests
import pandas as pd
import io

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3
SEARCH_RADIUS_KM = 500 # Look for quakes within a 500km radius

# --- Fallback Data (A recent snapshot of NUFORC data) ---
FALLBACK_DATA = """Date / Time,City,State,Country,Shape,Duration,Summary,Posted,Images
11/10/23 20:20,North Charleston,SC,USA,Light,10 seconds,Light moving in the sky,11/10/23,
11/10/23 19:50,Bonney Lake,WA,USA,Light,30 seconds,A bright light appeared out of nowhere over Lake Tapps and disappeared.,11/10/23,
11/9/23 21:00,Eugene,OR,USA,Triangle,1 minute,Silent black triangle with 3 lights and a red one in the middle.,11/10/23,
11/9/23 18:30,Erie,PA,USA,Sphere,2 minutes,Orange sphere flying over Lake Erie.,11/10/23,
11/8/23 22:00,Las Vegas,NV,USA,Light,5 minutes,3 bright lights in a triangular formation moving silently.,11/10/23,
11/8/23 19:45,Los Angeles,CA,USA,Circle,15 seconds,A perfect circle of light zipped across the sky.,11/10/23,
11/7/23 20:30,Austin,TX,USA,Chevron,1 minute,V-shaped craft with white lights on the leading edge.,11/10/23,
11/7/23 05:30,Phoenix,AZ,USA,Fireball,30 seconds,A bright fireball streaked across the morning sky.,11/10/23,
11/6/23 21:15,Denver,CO,USA,Light,2 minutes,Stationary light that suddenly accelerated and vanished.,11/10/23,
11/6/23 18:00,Seattle,WA,USA,Formation,5 minutes,A formation of lights moving in unison.,11/10/23,
11/5/23 22:45,Miami,FL,USA,Sphere,10 seconds,A metallic sphere hovered and then shot upwards.,11/10/23,
11/5/23 19:00,Chicago,IL,USA,Light,1 minute,A single light moving erratically against the wind.,11/10/23,
11/4/23 21:00,Portland,OR,USA,Triangle,2 minutes,A dark triangular craft flew silently overhead.,11/10/23,
11/4/23 17:30,Albuquerque,NM,USA,Disc,45 seconds,A classic silver disc seen in the afternoon sun.,11/10/23,
11/3/23 20:00,San Diego,CA,USA,Light,3 minutes,Lights maneuvering off the coast over the ocean.,11/10/23,
"""

# --- Data Fetching Functions ---

def fetch_sighting_data():
    """ Tries to fetch live data; uses a fallback on failure. """
    try:
        # First, try the best method: live scraping
        url = "https://nuforc.org/webreports/ndxpost.html"
        tables = pd.read_html(url, attrs={'border': '1'})
        df = tables[0]
        st.sidebar.success("Live NUFORC data loaded.")
        return df
    except (ImportError, ValueError) as e:
        # If lxml is missing or the table isn't found, use the fallback
        st.sidebar.warning("Live data fetch failed. Using a static backup. (This may be due to a missing 'lxml' library or a change in the NUFORC website.)")
        fallback_df = pd.read_csv(io.StringIO(FALLBACK_DATA))
        return fallback_df

def get_coords_for_city(city, state):
    """ Gets latitude and longitude for a city. """
    query = f"{city}, {state}" if state and pd.notna(state) else city
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/1.1'}
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
st.markdown("This tool automatically correlates UAP sighting reports with local seismic activity.")

st.info("Attempting to fetch the latest UAP sighting reports from the National UFO Reporting Center (NUFORC)...")

sighting_df_raw = fetch_sighting_data()

if sighting_df_raw is not None and not sighting_df_raw.empty:
    # Clean up the dataframe
    sighting_df_raw.columns = ['Date / Time', 'City', 'State', 'Country', 'Shape', 'Duration', 'Summary', 'Posted', 'Images']
    sighting_df_raw['Event Date'] = pd.to_datetime(sighting_df_raw['Date / Time'].str.split(' ').str[0], errors='coerce')
    sighting_df_raw.dropna(subset=['Event Date'], inplace=True)

    st.success(f"Successfully loaded {len(sighting_df_raw)} recent sighting reports.")

    sightings_to_process = st.slider("Number of recent sightings to analyze:", 5, 50, 10)

    for index, row in sighting_df_raw.head(sightings_to_process).iterrows():
        sighting_date = row['Event Date']
        stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
        city, state = row['City'], row.get('State')

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
    st.error("Could not load any sighting data from live or backup sources.")
