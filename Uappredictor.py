import streamlit as st
import datetime
import requests
import pandas as pd
import io
import math

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3

# --- Haversine Distance Function (No Dependencies) ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on Earth using the Haversine formula.
    """
    R = 6371 # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# --- Fallback Data ---
FALLBACK_DATA = """Date / Time,City,State,Country,Shape,Duration,Summary,Posted,Images
11/10/23 20:20,North Charleston,SC,USA,Light,10 seconds,Light moving in the sky,11/10/23,
11/10/23 19:50,Bonney Lake,WA,USA,Light,30 seconds,A bright light appeared out of nowhere over Lake Tapps and disappeared.,11/10/23,
11/9/23 21:00,Eugene,OR,USA,Triangle,1 minute,Silent black triangle with 3 lights and a red one in the middle.,11/10/23,
11/9/23 18:30,Erie,PA,USA,Sphere,2 minutes,Orange sphere flying over Lake Erie.,11/10/23,
11/8/23 22:00,Las Vegas,NV,USA,Light,5 minutes,3 bright lights in a triangular formation moving silently.,11/10/23,
11/8/23 19:45,Los Angeles,CA,USA,Circle,15 seconds,A perfect circle of light zipped across the sky.,11/10/23,
11/7/23 20:30,Austin,TX,USA,Chevron,1 minute,V-shaped craft with white lights on the leading edge.,11/10/23,
"""

# --- Data Fetching Functions ---

def fetch_sighting_data():
    try:
        url = "https://nuforc.org/webreports/ndxpost.html"
        tables = pd.read_html(url, attrs={'border': '1'})
        df = tables[0]
        st.sidebar.success("Live NUFORC data loaded.")
        return df
    except Exception as e:
        st.sidebar.warning(f"Live data failed. Using static backup.")
        return pd.read_csv(io.StringIO(FALLBACK_DATA))

def get_coords_for_city(city, state):
    query = f"{city}, {state}" if state and pd.notna(state) else city
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/1.3'} # Incremented version
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        return None, None

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
st.markdown("This tool automatically correlates UAP sightings with local seismic activity, including distance to the epicenter.")

st.sidebar.header("Analysis Parameters")
search_radius_km = st.sidebar.slider("Search Radius (km)", 100, 1000, 500, 50)
sightings_to_process = st.sidebar.slider("Number of recent sightings to analyze:", 5, 50, 10)

sighting_df_raw = fetch_sighting_data()

if sighting_df_raw is not None and not sighting_df_raw.empty:
    sighting_df_raw.columns = sighting_df_raw.columns.str.strip()
    sighting_df_raw['Event Date'] = pd.to_datetime(sighting_df_raw['Date / Time'].str.split(' ').str[0], errors='coerce')
    sighting_df_raw.dropna(subset=['Event Date'], inplace=True)
    st.success(f"Successfully loaded {len(sighting_df_raw)} recent sighting reports.")

    for index, row in sighting_df_raw.head(sightings_to_process).iterrows():
        sighting_date = row['Event Date']
        stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
        city, state = row['City'], row.get('State')

        st.write("---")
        st.subheader(f"Sighting: {city}, {state} on {sighting_date.strftime('%Y-%m-%d')}")
        st.caption(f"Summary: {row['Summary']}")

        with st.spinner(f"Analyzing geological data for {city}, {state}..."):
            sighting_coords = get_coords_for_city(city, state)
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
                st.error(f"Could not find coordinates for '{city}, {state}'. Skipping analysis.")
else:
    st.error("Could not load any sighting data.")
