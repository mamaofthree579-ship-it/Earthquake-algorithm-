import streamlit as st
import datetime
import requests
import pandas as pd

# --- Constants from the Paper ---
WEIGHT_SEISMIC = 0.6
WEIGHT_GEOMAGNETIC = 0.4
PSI_THRESHOLD = 80
PREDICTION_LAG_DAYS = 3

# --- Real Data Fetching Functions (No changes needed here) ---

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
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        event_count = data['metadata']['count']
        location, max_magnitude = (None, 0)
        if event_count > 0:
            largest_quake = max(data['features'], key=lambda x: x['properties']['mag'])
            max_magnitude = largest_quake['properties']['mag']
            coords = largest_quake['geometry']['coordinates']
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
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        kp_values_for_day = [float(row[1]) for row in data[1:] if row[0].startswith(date_str)]
        if kp_values_for_day:
            max_kp = max(kp_values_for_day)
            st.write(f"✔️ NOAA API Success: Found max Kp-index of {max_kp}.")
            return max_kp
        else:
            # Check if the requested date is simply too old for the 30-day API
            if datetime.datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.date.today() - datetime.timedelta(days=27):
                 st.error(f"❌ NOAA data for {date_str} is too old. The API only provides the last ~27 days of Kp data.")
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
st.caption("A validation tool for the 'Planetary Regulation System' theory.")

# --- Sidebar Controls ---
st.sidebar.header("Controls")
analysis_mode = st.sidebar.radio(
    "Select Analysis Mode",
    ('Live Prediction', 'Historical Analysis')
)

run_analysis = False
if analysis_mode == 'Live Prediction':
    st.sidebar.info("Predicts activity for today based on data from 3 days ago.")
    target_date = datetime.date.today()
    if st.sidebar.button('Generate Today\'s Prediction'):
        run_analysis = True
else: # Historical Analysis
    st.sidebar.info("Analyze the prediction for any specific date in the past.")
    target_date = st.sidebar.date_input(
        "Select Target Date for Analysis",
        datetime.date(2004, 11, 14), # Default to USS Nimitz encounter
        max_value=datetime.date.today()
    )
    if st.sidebar.button('Run Historical Analysis'):
        run_analysis = True

# --- Main App Body ---
if run_analysis:
    stimulus_date = target_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
    stimulus_date_str = stimulus_date.strftime("%Y-%m-%d")

    st.header(f"Analysis for: {target_date.strftime('%B %d, %Y')}")
    st.markdown(f"Planetary data is being fetched for the stimulus date: **{stimulus_date_str}** (3 days prior).")
    st.write("---")

    with st.spinner(f"Fetching live planetary data for {stimulus_date_str}..."):
        seismic_count, quake_location, quake_mag = fetch_real_earthquake_data(stimulus_date_str)
        kp_index = fetch_real_geomagnetic_data(stimulus_date_str)

    psi_value = calculate_psi(seismic_count, kp_index)

    st.subheader(f"Planetary Data Analysis for {stimulus_date_str}")
    col1, col2, col3 = st.columns(3)
    col1.metric("M6.0+ Earthquakes", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}", help="PSI = (0.6 * Quakes) + (0.4 * Kp-Index*10)")

    st.write("---")
    st.subheader(f"Conclusion for Target Date: {target_date.strftime('%B %d, %Y')}")

    if psi_value > PSI_THRESHOLD:
        st.warning(f"""
        **RESULT: HIGH PROBABILITY PREDICTED.**
        The model suggests a high likelihood of Guardian/UAP activity on this date.
        The PSI of **{psi_value:.2f}** recorded on {stimulus_date_str} exceeded the {PSI_THRESHOLD} threshold.
        """)
        if seismic_count > 0 and quake_location:
            st.subheader("Predicted Area of Interest")
            st.markdown(f"The primary trigger was a Magnitude **{quake_mag}** earthquake. Activity may have been concentrated near its epicenter.")
            map_data = pd.DataFrame([quake_location])
            st.map(map_data, zoom=4)
    else:
        st.success(f"""
        **RESULT: NOMINAL ACTIVITY PREDICTED.**
        The model suggests normal conditions. The PSI on {stimulus_date_str} was {psi_value:.2f}, which is below the activity threshold.
        """)
else:
    st.info("Select a mode and click the button in the sidebar to begin analysis.")
