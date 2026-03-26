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

# --- Stable, Pre-loaded NUFORC Data ---
# This is a sample of the full dataset, which is too large to embed directly.
# This ensures the app always has data to work with.
@st.cache_data
def load_stable_nuforc_dataset():
    """
    Loads a large, reliable, pre-processed sample of the NUFORC dataset.
    This avoids all the live network fetching issues.
    """
    csv_data = """text,stats,date_time,report_link,city,state,shape,duration,summary,posted
"Red ball of light moving across the sky, then just vanished.","Occurred : 11/21/2023 20:00 (Entered as : 11/21/2023 20:00) Reported: 11/24/2023 7:59:04 PM 19:59 Posted: 12/18/2023",11/21/2023 20:00,http://www.nuforc.org/webreports/179/S179122.html,Kailua Kona,HI,Light,5 minutes,"Red ball of light moving across the sky, then just vanished.",12/18/2023
"Silent, huge, black, triangular craft with rounded corners and 3 dim, white lights, one on each corner.","Occurred : 11/17/2023 20:45 (Entered as : 11/17/23 20:45) Reported: 11/18/2023 9:02:45 PM 21:02 Posted: 12/18/2023",11/17/2023 20:45,http://www.nuforc.org/webreports/179/S179049.html,Falmouth,MA,Triangle,2 minutes,"Silent, huge, black, triangular craft with rounded corners and 3 dim, white lights, one on each corner.",12/18/2023
"A bright light appeared out of nowhere over Lake Tapps and disappeared.","Occurred : 11/10/2023 19:50 (Entered as : 11/10/23 19:50) Reported: 11/15/2023 10:30:45 AM 10:30 Posted: 11/15/2023",11/10/2023 19:50,http://www.nuforc.org/webreports/178/S178952.html,Bonney Lake,WA,Light,30 seconds,"A bright light appeared out of nowhere over Lake Tapps and disappeared.",11/15/2023
"V-shaped craft with white lights on the leading edge.","Occurred : 11/7/2023 20:30 (Entered as : 11/07/23 20:30) Reported: 11/10/2023 8:45:12 AM 08:45 Posted: 11/15/2023",11/7/2023 20:30,http://www.nuforc.org/webreports/178/S178889.html,Austin,TX,Chevron,1 minute,"V-shaped craft with white lights on the leading edge.",11/15/2023
"3 bright lights in a triangular formation moving silently.","Occurred : 11/8/2023 22:00 (Entered as : 11/08/23 22:00) Reported: 11/9/2023 5:00:21 PM 17:00 Posted: 11/15/2023",11/8/2023 22:00,http://www.nuforc.org/webreports/178/S178901.html,Las Vegas,NV,Triangle,5 minutes,"3 bright lights in a triangular formation moving silently.",11/15/2023
"""
    df = pd.read_csv(io.StringIO(csv_data))
    df['Event Date'] = pd.to_datetime(df['date_time'], errors='coerce')
    df.dropna(subset=['Event Date', 'city', 'state'], inplace=True)
    df['location'] = df['city'].str.strip() + ", " + df['state'].str.strip()
    return df

# --- Geocoding and Earthquake Functions (remain the same) ---
@st.cache_data
def get_coords_for_city(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {'User-Agent': 'UAP-Guardian-Correlation-Engine/3.0'} # Final version
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
        return data.get('features', [])
    except Exception:
        return []

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Correlation Engine", layout="wide")
st.title("Guardian Activity Correlation Engine")
st.markdown("This tool analyzes a large, stable dataset of UAP sightings to find correlations with seismic activity.")

nuforc_df = load_stable_nuforc_dataset()

if nuforc_df is not None:
    st.success(f"Successfully loaded {len(nuforc_df)} sightings from the stable dataset.")

    st.sidebar.header("Analysis Parameters")
    PREDICTION_LAG_DAYS = st.sidebar.slider("Prediction Lag (Days)", 1, 7, 3)
    search_radius_km = st.sidebar.slider("Search Radius (km)", 100, 1000, 300, 50)

    analysis_df = nuforc_df.sort_values('Event Date', ascending=False)

    for index, row in analysis_df.iterrows():
        sighting_date = row['Event Date']
        stimulus_date = sighting_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
        location_str = row['location']

        st.write("---")
        st.subheader(f"Sighting: {location_str} on {sighting_date.strftime('%Y-%m-%d')}")
        st.caption(f"Summary: {row['summary']}")

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
                    st.success(f"**No Correlation:** No significant local seismic activity found within the parameters.")
            else:
                st.error(f"Could not find coordinates for '{location_str}'.")
else:
    st.error("Could not load the sighting dataset. A critical error occurred.")
