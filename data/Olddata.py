import requests, pandas as pd

def fetch_usgs(start, end):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"
        f"format=geojson&starttime={start}&endtime={end}&minmagnitude=4"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        st.error(f"USGS fetch failed: {e}")
        return pd.DataFrame() # empty, won’t clobber your file

    data = resp.json()
    rows = []
    for f in data.get("features", []):
        props = f["properties"]
        rows.append({
            "date": props["time"][:10],
            "time": props["time"][11:19],
            "place": props.get("place", "unknown"),
            "magnitude": props["mag"],
            "solar_flare_window": 0
        })
    return pd.DataFrame(rows)

old_df = fetch_usgs("2023-01-01", "2023-12-31")
if not old_df.empty:
    old_df.to_csv(Path(__file__).parents[1] / "data" / "sample_quakes.csv", index=False)
    st.success("Historical USGS data loaded")
else:
    st.warning("Kept existing CSV")
