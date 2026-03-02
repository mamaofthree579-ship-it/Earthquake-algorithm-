import pandas as pd

def fetch_enso_index():
    url = "https://psl.noaa.gov/data/correlation/oni.data"
    df = pd.read_fwf(url, skiprows=1)
    
    # latest row
    latest = df.iloc[-1]
    enso = latest[1:].mean()
    
    return float(enso)
    
