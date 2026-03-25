import streamlit as st
import datetime
import requests # Added for live API calls
import random # Still used in the API functions for fallback/errors

# --- Constants from the Paper ---
WEIGHT_SEISMIC = 0.6
WEIGHT_GEOMAGNETIC = 0.4
PSI_THRESHOLD = 80
PREDICTION_LAG_DAYS = 3

# --- Real Data Fetching Functions ---

def fetch_real_earthquake_data(date_str):
    """
    Fetches real seismic data from the USGS API for a given date.
    Counts the number of earthquakes with a magnitude of 6.0 or higher.
    """
    start_time = f"{date_str}T00:00:00"
    end_time = f"{date_str}T23:59:59"
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start_time}&endtime={end_time}&minmagnitude=6.0"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises an error for bad responses
        data = response.json()
        seismic_event_count = data['metadata']['count']
        st.write(f"✔️ USGS API Success: Found {seismic_event_count} M6.0+ events.")
        return seismic_event_count
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Could not connect to USGS API: {e}")
        return 0 # Return 0 on failure

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

        kp_values_for_day = []
        # Skip header row with [1:]
        for row in data[1:]:
            if row[0].startswith(date_str):
                kp_value = float(row[1])
                kp_values_for_day.append(kp_value)

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
    """
    Calculates the Planetary Stress Index (PSI).
    Scaling Kp-index by 10 for a more dynamic PSI.
    """
    # Note: The paper does not specify if the Kp-index should be scaled.
    # We scale it by 10 here to give it a comparable weight to seismic events.
    # This is a key parameter that could be tuned.
    psi = (WEIGHT_SEISMIC * seismic_event_count) + (WEIGHT_GEOMAGNETIC * (max_kp_index * 10))
    return psi

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Predictor", layout="wide")

st.title("Guardian Activity Predictor")
st.caption(f"Based on the 'Planetary Regulation System' theory. Today is {datetime.date.today()}.")

st.markdown("""
This app implements the predictive model described in the paper. It fetches live data
from the USGS and NOAA to calculate the Planetary Stress Index (PSI)
from **3 days ago** and uses it to predict the likelihood of 'Guardian' activity **today**.
""")

if st.button('Generate Today\'s Prediction'):

    # 1. Determine the date for the historical data
    prediction_date = datetime.date.today() - datetime.timedelta(days=PREDICTION_LAG_DAYS)
    prediction_date_str = prediction_date.strftime("%Y-%m-%d")

    with st.spinner(f"Fetching live planetary data for {prediction_date_str}..."):
        # 2. Fetch REAL data
        seismic_count = fetch_real_earthquake_data(prediction_date_str)
        kp_index = fetch_real_geomagnetic_data(prediction_date_str)

    # 3. Calculate the PSI
    psi_value = calculate_psi(seismic_count, kp_index)

    st.write("---")
    st.subheader(f"Analysis of Planetary Data for {prediction_date_str}")

    col1, col2, col3 = st.columns(3)
    col1.metric("M6.0+ Earthquakes", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}", help="PSI = (0.6 * Quakes) + (0.4 * Kp-Index*10)")

    st.write("---")
    st.subheader(f"Prediction for Today ({datetime.date.today()})")

    # 4. Generate and display the final prediction
    if psi_value > PSI_THRESHOLD:
        st.warning(f"""
        **ALERT: HIGH PROBABILITY** of Guardian/UAP activity predicted.
        A high PSI of **{psi_value:.2f}** was recorded 3 days ago, exceeding the {PSI_THRESHOLD} threshold.
        """)
    else:
        st.success(f"""
        **Nominal Activity Predicted.**
        The PSI 3 days ago was {psi_value:.2f}, which is below the activity threshold.
        """)
