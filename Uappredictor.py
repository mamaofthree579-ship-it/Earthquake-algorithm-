import streamlit as st
import datetime
import requests
import pandas as pd

# --- Constants & Defaults ---
PREDICTION_LAG_DAYS = 3

# --- Real Data Fetching Functions ---

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

def fetch_live_geomagnetic_data(date_str):
    """ Fetches live geomagnetic data, returns 0 if data is too old. """
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    if datetime.datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.date.today() - datetime.timedelta(days=27):
        st.warning(f"⚠️ Live NOAA data for {date_str} is too old. Use the manual override below.")
        return 0
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
            st.warning(f"⚠️ No live Kp-index data found for {date_str}.")
            return 0
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not connect to live NOAA API: {e}")
        return 0

# --- Core Logic ---
def calculate_psi(seismic_count, max_kp, seismic_weight, kp_multiplier):
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
        "Select Target Date", datetime.date(2004, 11, 14), max_value=datetime.date.today()
    )

st.sidebar.divider()

# --- Manual Kp-Index Override ---
st.sidebar.header("Historical Kp-Index")
manual_kp_override = st.sidebar.checkbox("Manually Enter Kp-Index")
manual_kp_value = 0
if manual_kp_override:
    st.sidebar.info("Look up the Kp-index from the official archive and enter the highest value for the stimulus date.")
    st.sidebar.markdown("[GFZ Potsdam Historical Kp Data](ftp://ftp.gfz-potsdam.de/pub/home/obs/kp-ap/wdc/monthly/)", unsafe_allow_html=True)
    manual_kp_value = st.sidebar.number_input("Max Kp-Index for Stimulus Date", min_value=0.0, max_value=9.0, step=0.1)

st.sidebar.divider()

# --- Model Parameter Controls ---
st.sidebar.header("Model Parameters")
seismic_weight = st.sidebar.slider("Seismic Weight", 0.0, 1.0, 0.6, 0.05)
kp_multiplier = st.sidebar.slider("Kp-Index Multiplier", 1, 20, 10)
psi_threshold = st.sidebar.slider("PSI Alert Threshold", 50, 150, 80)

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
        kp_index = 0
        if manual_kp_override:
            st.write(f"✔️ Manual Override: Using Kp-Index of {manual_kp_value}.")
            kp_index = manual_kp_value
        else:
            kp_index = fetch_live_geomagnetic_data(stimulus_date_str)

    psi_value = calculate_psi(seismic_count, kp_index, seismic_weight, kp_multiplier)
    geomagnetic_weight = 1.0 - seismic_weight
    psi_formula_help = (f"PSI = ({seismic_weight:.2f} * Quakes) + ({geomagnetic_weight:.2f} * Kp-Index * {kp_multiplier})")

    st.subheader(f"Planetary Data Analysis for {stimulus_date_str}")
    col1, col2, col3 = st.columns(3)
    col1.metric("M6.0+ Earthquakes", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}", help=psi_formula_help)

    st.write("---")
    st.subheader(f"Conclusion for Target Date: {target_date.strftime('%B %d, %Y')}")

    if psi_value > psi_threshold:
        st.warning(f"**RESULT: HIGH PROBABILITY PREDICTED.** The PSI of **{psi_value:.2f}** exceeded the threshold of **{psi_threshold}**.")
        if seismic_count > 0 and quake_loc:
            st.subheader("Predicted Area of Interest")
            st.markdown(f"A Magnitude **{quake_mag}** earthquake was a likely trigger. Activity may have been concentrated near its epicenter.")
            st.map(pd.DataFrame([quake_loc]), zoom=4)
    else:
        st.success(f"**RESULT: NOMINAL ACTIVITY PREDICTED.** The PSI of **{psi_value:.2f}** is below the threshold of **{psi_threshold}**.")
else:
    st.info("Adjust parameters and click 'Run Analysis' in the sidebar to begin.")
