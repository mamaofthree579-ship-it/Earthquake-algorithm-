import pytest
import requests
import json
from ingest import usgs
from datetime import datetime

# A small synthetic USGS-like GeoJSON fixture
USGS_SAMPLE = {
    "type": "FeatureCollection",
    "metadata": {"generated": 1},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mag": 4.5,
                "place": "100 km S of Example",
                "time": 1609459200000,  # 2021-01-01 00:00:00 UTC
                "url": "https://example"
            },
            "geometry": {"type": "Point", "coordinates": [-120.0, 35.0, 10.0]},
            "id": "usgs_test_1"
        }
    ]
}

class DummyResponse:
    def __init__(self, json_obj, status_code=200):
        self._json = json_obj
        self.status_code = status_code
    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError(f"Status {self.status_code}")
    def json(self):
        return self._json

def test_fetch_usgs_week_monkeypatch(monkeypatch):
    def fake_get(url, timeout=10):
        return DummyResponse(USGS_SAMPLE)
    monkeypatch.setattr("requests.get", fake_get)
    df = usgs.fetch_usgs_week()
    assert not df.empty
    assert list(df.columns) >= ["id", "time_utc", "magnitude", "place", "longitude", "latitude", "depth_km", "url"]
    # Check the magnitude and coordinates
    assert df.iloc[0]["magnitude"] == 4.5
    assert pytest.approx(df.iloc[0]["longitude"], 0.001) == -120.0
    assert isinstance(df.iloc[0]["time_utc"], datetime)
