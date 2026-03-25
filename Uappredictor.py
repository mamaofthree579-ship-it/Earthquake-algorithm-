import streamlit as st
import datetime
import requests
import pandas as pd # Added for map data

# --- Constants from the Paper ---
WEIGHT_SEISMIC = 0.6
WEIGHT_GEOMAGNETIC = 0.4
PSI_THRESHOLD = 80
PREDICTION_LAG_DAYS = 3

# --- Real Data Fetching Functions (with Location) ---

def fetch_real_earthquake_data(date_str):
    """
    Fetches real seismic data from the USGS API for a given date.
    Counts M6.0+ events and finds the location of the largest one.
    """
    start_time = f"{date_str}T00:00:00"
    end_time = f"{date_str}T23:59:59"
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}&minmagnitude=6.0"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        event_count = data['metadata']['count']

        location = None
        max_magnitude = 0

        if event_count > 0:
            # Find the largest earthquake to use as the location marker
            largest_quake = max(data['features'], key=lambda x: x['properties']['mag'])
            max_magnitude = largest_quake['properties']['mag']
            coords = largest_quake['geometry']['coordinates']
            # GeoJSON format is [longitude, latitude]
            location = {'lat': coords[1], 'lon': coords[0]}

        st.write(f"✔️ USGS API Success: Found {event_count} M6.0+ events.")
        return event_count, location, max_magnitude

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not connect to USGS API: {e}")
        return 0, None, 0

def fetch_real_geomagnetic_data(date_str):
    """
    Fetches real geomagnetic data from the NOAA SWPC API.
    Finds the maximum Kp-index for a given date.
    """
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        kp_values_for_day = [float(row[1]) for row in data[1:] if row[0].startswith(date_str)]

        if kp_values_for_day:
            max_kp = max(kp_values_for_day)
            st.write(f"✔️ NOAA API Success: Found max Kp-index of {max_kp}.")
            return max_kp
        else:
            st.warning(f"⚠️ No Kp-index data found for {date_str} in NOAA's recent data.")
            return 0
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not connect to NOAA API: {e}")
        return 0

# --- Core Logic ---
def calculate_psi(seismic_event_count, max_kp_index):
    """ Calculates the Planetary Stress Index (PSI). """
    psi = (WEIGHT_SEISMIC * seismic_event_count) + (WEIGHT_GEOMAGNETIC * (max_kp_index * 10))
    return psi

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Predictor", layout="wide")

st.title("Guardian Activity Predictor")
st.caption(f"Based on the 'Planetary Regulation System' theory. Today is {datetime.date.today()}.")

st.markdown("""
This app implements the predictive model from the paper, now with location-specific predictions.
It fetches live data to calculate the PSI from **3 days ago** to predict Guardian activity **today**.
""")

if st.button('Generate Today\'s Prediction'):

    prediction_date = datetime.date.today() - datetime.timedelta(days=PREDICTION_LAG_DAYS)
    prediction_date_str = prediction_date.strftime("%Y-%m-%d")

    with st.spinner(f"Fetching live planetary data for {prediction_date_str}..."):
        seismic_count, quake_location, quake_mag = fetch_real_earthquake_data(prediction_date_str)
        kp_index = fetch_real_geomagnetic_data(prediction_date_str)

    psi_value = calculate_psi(seismic_count, kp_index)

    st.write("---")
    st.subheader(f"Analysis of Planetary Data for {prediction_date_str}")

    col1, col2, col3 = st.columns(3)
    col1.metric("M6.0+ Earthquakes", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}", help="PSI = (0.6 * Quakes) + (0.4 * Kp-Index*10)")

    st.write("---")
    st.subheader(f"Prediction for Today ({datetime.date.today()})")

    if psi_value > PSI_THRESHOLD:
        st.warning(f"""
        **ALERT: HIGH PROBABILITY** of Guardian/UAP activity predicted.
        A high PSI of **{psi_value:.2f}** was recorded 3 days ago, exceeding the {PSI_THRESHOLD} threshold.
        """)
        # If the alert was triggered by a seismic event, show the map
        if seismic_count > 0 and quake_location:
            st.subheader("Predicted Area of Interest")
            st.markdown(f"The primary trigger was a Magnitude **{quake_mag}** earthquake. Activity may be concentrated near its epicenter.")
            map_data = pd.DataFrame([quake_location])
            st.map(map_data, zoom=5)
    else:
        st.success(f"""
        **Nominal Activity Predicted.**
        The PSI 3 days ago was {psi_value:.2f}, which is below the activity threshold.
        """)
