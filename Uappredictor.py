import streamlit as st
import datetime
import random

# --- Constants from the Paper ---
WEIGHT_SEISMIC = 0.6
WEIGHT_GEOMAGNETIC = 0.4
PSI_THRESHOLD = 80
PREDICTION_LAG_DAYS = 3

# --- Mock Data Fetching Functions ---
# (You will still replace these with real API calls)
def fetch_earthquake_data(date_str):
    """
    Placeholder for USGS API call.
    Returns a mock count of M6.0+ earthquakes.
    """
    # Simulate a rare major event for demonstration
    if random.random() < 0.2: # 20% chance of a quake for the demo
        return random.choices([1, 2], weights=[90, 10], k=1)[0]
    return 0

def fetch_geomagnetic_data(date_str):
    """
    Placeholder for NOAA SWPC API call.
    Returns a mock maximum Kp-index.
    """
    # Simulate a rare major event for demonstration
    if random.random() < 0.2: # 20% chance of a storm for the demo
        return random.randint(5, 9)
    return random.randint(1, 4)

# --- Core Logic from the Paper ---
def calculate_psi(seismic_event_count, max_kp_index):
    """
    Calculates the Planetary Stress Index (PSI).
    Scaling Kp-index by 10 for a more dynamic PSI as discussed.
    """
    psi = (WEIGHT_SEISMIC * seismic_event_count) + (WEIGHT_GEOMAGNETIC * (max_kp_index * 10))
    return psi

# --- Streamlit App UI ---
st.set_page_config(page_title="Guardian Predictor", layout="wide")

st.title("Guardian Activity Predictor")
st.caption(f"Based on the 'Planetary Regulation System' theory. Today is {datetime.date.today()}.")

st.markdown("""
This app simulates the prediction model from the paper. It calculates the Planetary Stress Index (PSI)
from **3 days ago** to predict the likelihood of 'Guardian' activity **today**.
""")

# Create a button to run the prediction
if st.button('Generate Today\'s Prediction'):

    # 1. Determine the date for the historical data
    prediction_date = datetime.date.today() - datetime.timedelta(days=PREDICTION_LAG_DAYS)
    prediction_date_str = prediction_date.strftime("%Y-%m-%d")

    # Use placeholders for the UI
    st.info(f"Fetching data for {prediction_date_str} (3-day lag)...")

    # 2. Fetch the data (using mock functions for now)
    seismic_count = fetch_earthquake_data(prediction_date_str)
    kp_index = fetch_geomagnetic_data(prediction_date_str)

    # 3. Calculate the PSI
    psi_value = calculate_psi(seismic_count, kp_index)

    st.write("---")
    st.subheader(f"Analysis for {prediction_date_str}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Major Earthquakes (Ns)", f"{seismic_count}")
    col2.metric("Max Geomagnetic Kp-Index", f"{kp_index}")
    col3.metric("Calculated PSI", f"{psi_value:.2f}")

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
