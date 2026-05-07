"""Tests for the CLI (__main__.py)."""

import json
from unittest.mock import patch

from meteofrance_api.__main__ import _local

import pytest

from meteofrance_api.__main__ import main
from meteofrance_api.const import METEOFRANCE_API_URL

BASE = METEOFRANCE_API_URL

PLACES_RESPONSE = [
    {
        "name": "Paris",
        "lat": 48.85341,
        "lon": 2.3488,
        "country": "FR",
        "admin": "Île-de-France",
        "admin2": "75",
        "postCode": "75000",
    }
]

FORECAST_RESPONSE = {
    "update_time": "2020-05-20T17:00:00.000Z",
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.3488, 48.85341]},
    "properties": {
        "altitude": 35,
        "name": "Paris",
        "country": "FR - France",
        "french_department": "75",
        "rain_product_available": 1,
        "timezone": "Europe/Paris",
        "daily_forecast": [
            {
                "time": "2020-05-20T00:00:00.000Z",
                "T_min": 12.0,
                "T_max": 22.0,
                "daily_weather_description": "Ensoleillé",
            },
        ],
        "forecast": [
            {
                "time": "2020-05-20T15:00:00.000Z",
                "T": 20.0,
                "weather_description": "Ensoleillé",
                "wind_speed": 10,
            },
        ],
    },
}

RAIN_RESPONSE = {
    "update_time": "2020-05-20T17:00:00.000Z",
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.3488, 48.85341]},
    "properties": {
        "altitude": 35,
        "name": "Paris",
        "country": "FR - France",
        "french_department": "75",
        "rain_product_available": 1,
        "timezone": "Europe/Paris",
        "confidence": 1,
        "forecast": [
            {
                "time": "2020-05-20T17:00:00.000Z",
                "rain_intensity": 1,
                "rain_intensity_description": "Temps sec",
            },
        ],
    },
}

OBSERVATION_RESPONSE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.3488, 48.85341]},
    "properties": {
        "timezone": "Europe/Paris",
        "gridded": {
            "time": "2020-05-20T15:00:00.000+0200",
            "T": 20.0,
            "wind_speed": 10.0,
            "wind_direction": 180,
            "weather_description": "Ensoleillé",
        },
    },
}

WARNING_PHENOMENONS_RESPONSE = {
    "update_time": 1591279200,
    "end_validity_time": 1591365600,
    "domain_id": "75",
    "phenomenons_max_colors": [
        {"phenomenon_id": "1", "phenomenon_max_color_id": 1},
        {"phenomenon_id": "3", "phenomenon_max_color_id": 2},
    ],
}

WARNING_DICTIONARY_RESPONSE = {
    "phenomenons": [
        {"id": 1, "name": "Vent violent"},
        {"id": 3, "name": "Orages"},
    ],
    "colors": [
        {"id": 1, "level": 1, "name": "vert", "hexaCode": "#31aa35"},
        {"id": 2, "level": 2, "name": "jaune", "hexaCode": "#fff600"},
    ],
}


def run(*argv: str) -> None:
    """Run main() with the given CLI arguments."""
    with patch("sys.argv", ["meteofrance-api", *argv]):
        main()


# ---------------------------------------------------------------------------
# places
# ---------------------------------------------------------------------------

def test_places_text(requests_mock, capsys) -> None:
    """Places command outputs text results."""
    requests_mock.get(f"{BASE}/v2/places", json=PLACES_RESPONSE)
    run("places", "Paris")
    out = capsys.readouterr().out
    assert "Paris" in out
    assert "75000" in out


def test_places_json(requests_mock, capsys) -> None:
    """Places command outputs JSON."""
    requests_mock.get(f"{BASE}/v2/places", json=PLACES_RESPONSE)
    run("--json", "places", "Paris")
    data = json.loads(capsys.readouterr().out)
    assert data[0]["name"] == "Paris"


def test_places_no_results(requests_mock, capsys) -> None:
    """Places command prints 'No results' when API returns empty list."""
    requests_mock.get(f"{BASE}/v2/places", json=[])
    run("places", "ZZZ")
    assert "No results" in capsys.readouterr().out


def test_places_text_no_admin_no_postal(requests_mock, capsys) -> None:
    """Places command handles missing admin and postal_code gracefully."""
    requests_mock.get(f"{BASE}/v2/places", json=[
        {"name": "Somewhere", "lat": 10.0, "lon": 20.0, "country": "XX"},
    ])
    run("places", "Somewhere")
    assert "Somewhere" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# forecast
# ---------------------------------------------------------------------------

def test_forecast_text(requests_mock, capsys) -> None:
    """Forecast command outputs text with lat/lon."""
    requests_mock.get(f"{BASE}/v2/forecast", json=FORECAST_RESPONSE)
    run("forecast", "--lat", "48.85", "--lon", "2.35")
    out = capsys.readouterr().out
    assert "Paris" in out
    assert "20.0°C" in out


def test_forecast_json(requests_mock, capsys) -> None:
    """Forecast command outputs JSON."""
    requests_mock.get(f"{BASE}/v2/forecast", json=FORECAST_RESPONSE)
    run("--json", "forecast", "--lat", "48.85", "--lon", "2.35")
    data = json.loads(capsys.readouterr().out)
    assert data["position"]["name"] == "Paris"


def test_forecast_place(requests_mock, capsys) -> None:
    """Forecast command resolves location via --place."""
    requests_mock.get(f"{BASE}/v2/places", json=PLACES_RESPONSE)
    requests_mock.get(f"{BASE}/v2/forecast", json=FORECAST_RESPONSE)
    run("forecast", "--place", "Paris")
    assert "Paris" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# rain
# ---------------------------------------------------------------------------

def test_rain_text(requests_mock, capsys) -> None:
    """Rain command outputs text."""
    requests_mock.get(f"{BASE}/v3/rain", json=RAIN_RESPONSE)
    run("rain", "--lat", "48.85", "--lon", "2.35")
    out = capsys.readouterr().out
    assert "Paris" in out
    assert "Confidence" in out


def test_rain_json(requests_mock, capsys) -> None:
    """Rain command outputs JSON."""
    requests_mock.get(f"{BASE}/v3/rain", json=RAIN_RESPONSE)
    run("--json", "rain", "--lat", "48.85", "--lon", "2.35")
    data = json.loads(capsys.readouterr().out)
    assert data["position"]["name"] == "Paris"
    assert "next_rain" in data


def test_rain_text_with_rain_expected(requests_mock, capsys) -> None:
    """Rain command shows next rain time when rain is expected."""
    rain_coming = {
        **RAIN_RESPONSE,
        "properties": {
            **RAIN_RESPONSE["properties"],
            "forecast": [
                {"time": "2020-05-20T17:00:00.000Z", "rain_intensity": 2,
                 "rain_intensity_description": "Pluie faible"},
            ],
        },
    }
    requests_mock.get(f"{BASE}/v3/rain", json=rain_coming)
    run("rain", "--lat", "48.85", "--lon", "2.35")
    assert "Next rain" in capsys.readouterr().out


def test_rain_unavailable(requests_mock, capsys) -> None:
    """Rain command exits with error when zone not covered."""
    requests_mock.get(f"{BASE}/v3/rain", json={})
    with pytest.raises(SystemExit):
        run("rain", "--lat", "45.0", "--lon", "-73.0")
    assert "unavailable" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# observation
# ---------------------------------------------------------------------------

def test_observation_text(requests_mock, capsys) -> None:
    """Observation command outputs text."""
    requests_mock.get(f"{BASE}/v2/observation", json=OBSERVATION_RESPONSE)
    run("observation", "--lat", "48.85", "--lon", "2.35")
    out = capsys.readouterr().out
    assert "20.0°C" in out
    assert "Ensoleillé" in out


def test_observation_json(requests_mock, capsys) -> None:
    """Observation command outputs JSON."""
    requests_mock.get(f"{BASE}/v2/observation", json=OBSERVATION_RESPONSE)
    run("--json", "observation", "--lat", "48.85", "--lon", "2.35")
    data = json.loads(capsys.readouterr().out)
    assert data["temperature"] == 20.0


# ---------------------------------------------------------------------------
# warning
# ---------------------------------------------------------------------------

def test_warning_text(requests_mock, capsys) -> None:
    """Warning command outputs text."""
    requests_mock.get(f"{BASE}/v3/warning/currentphenomenons", json=WARNING_PHENOMENONS_RESPONSE)
    requests_mock.get(f"{BASE}/v3/warning/dictionary", json=WARNING_DICTIONARY_RESPONSE)
    run("warning", "75")
    out = capsys.readouterr().out
    assert "75" in out
    assert "Vent violent" in out


def test_warning_json(requests_mock, capsys) -> None:
    """Warning command outputs JSON."""
    requests_mock.get(f"{BASE}/v3/warning/currentphenomenons", json=WARNING_PHENOMENONS_RESPONSE)
    requests_mock.get(f"{BASE}/v3/warning/dictionary", json=WARNING_DICTIONARY_RESPONSE)
    run("--json", "warning", "75")
    data = json.loads(capsys.readouterr().out)
    assert data["domain_id"] == "75"
    assert data["phenomenons"][0]["name"] == "Vent violent"


# ---------------------------------------------------------------------------
# picture
# ---------------------------------------------------------------------------

def test_picture_text(requests_mock, capsys) -> None:
    """Picture command outputs URL and description."""
    requests_mock.get(f"{BASE}/v2/report", text="Belle photo du jour.")
    run("picture")
    out = capsys.readouterr().out
    assert "URL" in out
    assert "Belle photo du jour." in out


def test_picture_json(requests_mock, capsys) -> None:
    """Picture command outputs JSON."""
    requests_mock.get(f"{BASE}/v2/report", text="Belle photo du jour.")
    run("--json", "picture")
    data = json.loads(capsys.readouterr().out)
    assert "image_url" in data
    assert data["description"] == "Belle photo du jour."


EPHEMERIS_RESPONSE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [6.170872, 46.017776]},
    "properties": {
        "ephemeris": {
            "sunrise_time": "2026-05-07T04:15:06.247Z",
            "sunset_time": "2026-05-07T18:51:13.688Z",
            "moonrise_time": "2026-05-08T00:18:21.829Z",
            "moonset_time": "2026-05-07T08:03:45.871Z",
            "moon_phase": "0.68",
            "moon_phase_description": "Lune Gibbeuse Décroissante",
            "saint": "Sainte Gisèle",
        }
    },
}


# ---------------------------------------------------------------------------
# ephemeris
# ---------------------------------------------------------------------------

def test_ephemeris_text(requests_mock, capsys) -> None:
    """Ephemeris command outputs text."""
    requests_mock.get(f"{BASE}/v2/ephemeris", json=EPHEMERIS_RESPONSE)
    run("ephemeris", "--lat", "46.017776", "--lon", "6.170872")
    out = capsys.readouterr().out
    assert "Sunrise" in out
    assert "Sainte Gisèle" in out


def test_ephemeris_json(requests_mock, capsys) -> None:
    """Ephemeris command outputs JSON."""
    requests_mock.get(f"{BASE}/v2/ephemeris", json=EPHEMERIS_RESPONSE)
    run("--json", "ephemeris", "--lat", "46.017776", "--lon", "6.170872")
    data = json.loads(capsys.readouterr().out)
    assert data["saint"] == "Sainte Gisèle"
    assert data["sunrise_time"] == "2026-05-07T04:15:06.247Z"


# ---------------------------------------------------------------------------
# _resolve_coords error paths
# ---------------------------------------------------------------------------

def test_resolve_coords_place_not_found(requests_mock, capsys) -> None:
    """Exits with error when place search returns nothing."""
    requests_mock.get(f"{BASE}/v2/places", json=[])
    with pytest.raises(SystemExit):
        run("forecast", "--place", "Inexistant")
    assert "No place found" in capsys.readouterr().err


def test_resolve_coords_no_args(capsys) -> None:
    """Exits with error when neither lat/lon nor place is provided."""
    with pytest.raises(SystemExit):
        run("forecast")
    assert "Provide" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# _local helper
# ---------------------------------------------------------------------------

def test_local_none() -> None:
    """_local returns 'N/A' when given None."""
    assert _local(None) == "N/A"
