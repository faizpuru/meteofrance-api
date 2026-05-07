"""Tests Météo-France module. Rain class."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from meteofrance_api import MeteoFranceClient
from meteofrance_api.const import METEOFRANCE_API_URL
from meteofrance_api.model.rain import RainForecastEntry
from meteofrance_api.model.rain import RainPosition

RAIN_V2_RESPONSE = {
    "update_time": "2020-05-20T17:00:00.000Z",
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.239895, 48.807166]},
    "properties": {
        "altitude": 76,
        "name": "Meudon",
        "country": "FR - France",
        "french_department": "92",
        "rain_product_available": 1,
        "timezone": "Europe/Paris",
        "confidence": 0,
        "forecast": [
            {"time": "2020-05-20T17:45:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
            {"time": "2020-05-20T17:50:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
            {"time": "2020-05-20T17:55:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
            {"time": "2020-05-20T17:50:00.000Z", "rain_intensity": 2,
             "rain_intensity_description": "Pluie faible"},
            {"time": "2020-05-20T17:55:00.000Z", "rain_intensity": 3,
             "rain_intensity_description": "Pluie modérée"},
            {"time": "2020-05-20T18:00:00.000Z", "rain_intensity": 2,
             "rain_intensity_description": "Pluie faible"},
            {"time": "2020-05-20T18:10:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
            {"time": "2020-05-20T18:20:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
            {"time": "2020-05-20T18:30:00.000Z", "rain_intensity": 1,
             "rain_intensity_description": "Temps sec"},
        ],
    },
}


def test_rain() -> None:
    """Test rain forecast on a covered zone."""
    client = MeteoFranceClient()

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)

    assert isinstance(rain.position, RainPosition)
    assert isinstance(rain.updated_on, int)
    assert isinstance(rain.confidence, int)
    assert isinstance(rain.forecast[0], RainForecastEntry)


def test_rain_not_covered() -> None:
    """Test rain forecast result on a non covered zone."""
    client = MeteoFranceClient()

    with pytest.raises(ValueError, match="not available"):
        client.get_rain(latitude=45.51, longitude=-73.58)


def test_rain_expected(requests_mock: Mock) -> None:
    """Test date computation when rain is expected within the hour."""
    client = MeteoFranceClient()

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json=RAIN_V2_RESPONSE,
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)

    assert rain.position.name == "Meudon"
    date_rain = rain.next_rain_date_locale()
    assert str(date_rain) == "2020-05-20 19:50:00+02:00"
    assert (
        str(rain.iso_to_locale_time(rain.forecast[3].time))
        == "2020-05-20 19:50:00+02:00"
    )


def test_rain_timestamp_to_locale_time(requests_mock: Mock) -> None:
    """Test conversion of a Unix timestamp to locale datetime on a Rain."""
    client = MeteoFranceClient()
    requests_mock.request("get", f"{METEOFRANCE_API_URL}/v3/rain", json=RAIN_V2_RESPONSE)
    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    dt = rain.timestamp_to_locale_time(1591279200)
    assert isinstance(dt, datetime)
    assert str(dt) == "2020-06-04 16:00:00+02:00"


def test_no_rain_expected(requests_mock: Mock) -> None:
    """Test date computation when no rain is expected within the hour."""
    client = MeteoFranceClient()

    no_rain_response = {
        **RAIN_V2_RESPONSE,
        "properties": {
            **RAIN_V2_RESPONSE["properties"],
            "forecast": [
                {"time": f"2020-05-20T17:{m:02d}:00.000Z", "rain_intensity": 1,
                 "rain_intensity_description": "Temps sec"}
                for m in range(45, 54, 5)
            ],
        },
    }

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json=no_rain_response,
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)

    assert rain.position.name == "Meudon"
    assert rain.next_rain_date_locale() is None
