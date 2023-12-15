# coding: utf-8
"""Tests Météo-France module. Forecast class."""
from datetime import datetime
from unittest.mock import Mock

from meteofrance_api import MeteoFranceClient
from meteofrance_api.const import METEOFRANCE_API_URL


def test_rain() -> None:
    """Test rain forecast on a covered zone."""
    client = MeteoFranceClient()

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    assert rain is not None
    assert isinstance(rain.altitude, int)
    assert isinstance(rain.update_time, datetime)
    assert isinstance(rain.location_name, str)
    assert isinstance(rain.geometry, dict)
    assert "type" in rain.geometry
    assert isinstance(rain.geometry["type"], str)
    assert "coordinates" in rain.geometry
    assert isinstance(rain.geometry["coordinates"], list)
    assert len(rain.geometry["coordinates"]) == 2
    assert all(isinstance(coord, float) for coord in rain.geometry["coordinates"])
    assert isinstance(rain.country, str)
    assert isinstance(rain.french_department, str)
    assert isinstance(rain.rain_product_available, int)
    assert isinstance(rain.confidence, int)

    assert "rain_intensity" in rain.forecasts[0].keys()


def test_rain_not_covered() -> None:
    """Test rain forecast result on a non covered zone."""
    client = MeteoFranceClient()
    rain = client.get_rain(latitude=45.508, longitude=-73.58)
    assert rain is None


def test_rain_expected(requests_mock: Mock) -> None:
    """Test datecomputation when rain is expected within the hour."""
    client = MeteoFranceClient()

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json={
            "update_time": 1702567200,
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
                    {
                        "time": 1702568100,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702568400,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702568700,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702569000,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702569300,
                        "rain_intensity": 2,
                        "rain_intensity_description": "Pluie faible",
                    },
                    {
                        "time": 1702569600,
                        "rain_intensity": 3,
                        "rain_intensity_description": "Pluie modérée",
                    },
                    {
                        "time": 1702570200,
                        "rain_intensity": 2,
                        "rain_intensity_description": "Pluie faible",
                    },
                    {
                        "time": 1702570800,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702571400,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                ],
            },
        },
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    assert rain is not None
    date_rain = rain.next_rain_date_locale()
    assert str(date_rain) == "2023-12-14 16:55:00+01:00"
    assert (
        str(rain.timestamp_to_locale_time(rain.forecasts[3]["time"]))
        == "2023-12-14 16:50:00+01:00"
    )


def test_no_rain_expected(requests_mock: Mock) -> None:
    """Test datecomputation when rain is expected within the hour."""
    client = MeteoFranceClient()

    requests_mock.request(
        "get",
        f"{METEOFRANCE_API_URL}/v3/rain",
        json={
            "update_time": 1702567200,
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
                    {
                        "time": 1702568100,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702568400,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702568700,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702569000,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702569300,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702569600,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702570200,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702570800,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                    {
                        "time": 1702571400,
                        "rain_intensity": 1,
                        "rain_intensity_description": "Temps sec",
                    },
                ],
            },
        },
    )

    rain = client.get_rain(latitude=48.8075, longitude=2.24028)
    assert rain is not None
    assert rain.next_rain_date_locale() is None
