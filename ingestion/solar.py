import requests

def fetch_kp_index():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    r = requests.get(url)
    data = r.json()
    latest = data[-1]
    return float(latest[1])
