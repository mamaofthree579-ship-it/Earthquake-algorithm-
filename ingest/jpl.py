"""
Simple JPL HORIZONS example stub.
This file shows how to call the JPL SSD API (REST) for ephemeris text samples.
For robust usage, use astroquery or the official SSD/HORIZONS endpoints with rate limiting.
"""
import requests

# Example JPL API endpoint for SSD/HORIZONS-like minimal usage: this is illustrative.
# For production, use JPL HORIZONS REST endpoints or astroquery.horizons.
JPL_EXAMPLE_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"  # Small-body DB (example)

def get_example_ephemeris(body="C/2025 A1"):
    """
    Fetch an example small-body record (note: this endpoint returns JSON metadata, not full HORIZONS ephemeris).
    Replace with proper HORIZONS ephemeris queries for position/time series.
    """
    params = {"sstr": body}
    r = requests.get(JPL_EXAMPLE_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.text
