import requests, pandas as pd

def fetch_usgs(start, end):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}"
    )
    data = requests.get(url).json()
    rows = []
    for f in data["features"]:
        props = f["properties"]
        rows.append({
            "date": props["time"][:10],
            "time": props["time"][11:19],
            "place": props["place"],
            "magnitude": props["mag"],
            "solar_flare_window": 0  # fill in later if you have flare data
        })
    return pd.DataFrame(rows)

# example: past year
old_df = fetch_usgs("2024-01-01", "2024-12-31")
old_df.to_csv("data/sample_quakes.csv", index=False)
