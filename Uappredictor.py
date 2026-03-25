import streamlit as st
import datetime
import requests
import pandas as pd

# --- Default Model Parameters (will be overridden by sidebar) ---
DEFAULT_WEIGHT_SEISMIC = 0.6
DEFAULT_KP_MULTIPLIER = 10
DEFAULT_PSI_THRESHOLD = 80
PREDICTION_LAG_DAYS = 3

# --- Real Data Fetching Functions (No changes) ---

def fetch_real_earthquake_data(date_str):
    """ Fetches real seismic data from the USGS API. """
    start_time = f"{date_str}T00:00:00"
    end_time = f"{date_str}T23:59:59"
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}&minmagnitude=6.0"
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
    """ Fetches real geomagnetic data from the NOAA SWPC API. """
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
            if datetime.datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.date.today() - datetime.timedelta(days=27):
                st.error(f"❌ NOAA data for {date_str} is >27 days old and not available via this API.")
            else:
                st.warning(f"⚠️ No Kp-index data found for {date_str} in NOAA's recent data.")
            return 0
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not connect to NOAA API: {e}")
        return 0

# --- Core Logic (Now accepts parameters) ---
def calculate_psi(seismic_count, max_kp, seismic_weight, kp_multiplier):
    """ Calculates the PSI using adjustable parameters. """
    geomagnetic_weight = 1.0 - seismic_weight
    psi = (seismic_weight * seismic_count) + (geomagnetic_weight * (max_kp * kp_multiplier))
    return psi

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Predictor", layout="wide")
st.title("Guardian Activity Simulator")
st.caption("A dynamic research tool for the 'Planetary Regulation System' theory.")

# --- Sidebar Controls ---
st.sidebar.header("Analysis Controls")
analysis_mode = st.sidebar.radio("Mode", ('Live Prediction', 'Historical Analysis'))

target_date = datetime.date.today()
if analysis_mode == 'Historical Analysis':
    target_date = st.sidebar.date_input(
        "Select Target Date",
        datetime.date(2004, 11, 14), # Default to USS Nimitz
        max_value=datetime.date.today()
    )

st.sidebar.divider()
st.sidebar.header("Model Parameters")
seismic_weight = st.sidebar.slider(
    "Seismic Weight", 0.0, 1.0, DEFAULT_WEIGHT_SEISMIC, 0.05,
    help="Adjust the influence of earthquakes. Geomagnetic weight will be the remainder."
)
kp_multiplier = st.sidebar.slider(
    "Kp-Index Multiplier", 1, 20, DEFAULT_KP_MULTIPLIER,
    help="Scales the geomagnetic score to make it comparable to seismic events."
)
psi_threshold = st.sidebar.slider(
    "PSI Alert Threshold", 50, 150, DEFAULT_PSI_THRESHOLD,
    help="The PSI value above which a 'High Probability' alert is triggered."
)

run_analysis = st.sidebar.button('Run Analysis', type="primary")

# --- Main App Body ---
if run_analysis:
    stimulus_date = target_date - datetime.timedelta(days=PREDICTION_LAG_DAYS)
    stimulus_date_str = stimulus_date.strftime("%Y-%m-%d")

    st.header(f"Analysis for: {target_date.strftime('%B %d, %Y')}")
    st.markdown(f"Planetary data is being fetched for the stimulus date: **{stimulus_date_str}**.")
    st.write("---")

    with st.spinner(f"Fetching planetary data for {stimulus_date_str}..."):
        seismic_count, quake_loc, quake_mag = fetch_real_earthquake_data(stimulus_date_str)
        kp_index = fetch_real_geomagnetic_data(stimulus_date_str)

    # --- FIX WAS HERE ---
    # Now correctly passing the slider values into the calculation.
    psi_value = calculate_psi(seismic_count, kp_index, seismic_weight, kp_multiplier)

    # Also dynamically creating the formula for the tooltip
    geomagnetic_weight = 1.0 - seismic_weight
    psi_formula_help = (f"PSI = ({seismic_weight:.2f} * Quakes) + ({geomagnetic_weight:.2f} * Kp-Index * {kp_multiplier})")

    st.subheader(f"Planetary Data Analysis for {stimulus_date_str}")
    col1, col2, col3 = st.columns(3)
    col1.metric("M6.0+ Earthquakes", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}", help=psi_formula_help)

    st.write("---")
    st.subheader(f"Conclusion for Target Date: {target_date.strftime('%B %d, %Y')}")

    # And using the custom psi_threshold for the comparison
    if psi_value > psi_threshold:
        st.warning(f"**RESULT: HIGH PROBABILITY PREDICTED.** The model suggests a high likelihood of activity on this date. The PSI of **{psi_value:.2f}** exceeded the custom threshold of **{psi_threshold}**.")
        if seismic_count > 0 and quake_loc:
            st.subheader("Predicted Area of Interest")
            st.markdown(f"A Magnitude **{quake_mag}** earthquake was the primary trigger. Activity may have been concentrated near its epicenter.")
            st.map(pd.DataFrame([quake_loc]), zoom=4)
    else:
        st.success(f"**RESULT: NOMINAL ACTIVITY PREDICTED.** The PSI of **{psi_value:.2f}** is below the custom threshold of **{psi_threshold}**.")
else:
    st.info("Adjust parameters and click 'Run Analysis' in the sidebar to begin.")
