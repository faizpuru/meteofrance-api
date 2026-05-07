"""Tests Météo-France module. Forecast class."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest.mock import Mock

from .const import MOUNTAIN_CITY
from meteofrance_api import MeteoFranceClient
from meteofrance_api.const import METEOFRANCE_API_URL
from meteofrance_api.model import Place
from meteofrance_api.model.forecast import DailyForecast
from meteofrance_api.model.forecast import ForecastPosition
from meteofrance_api.model.forecast import HourlyForecast
from meteofrance_api.model.forecast import ProbabilityForecast

FORECAST_PAST_RESPONSE = {
    "update_time": "2020-05-20T17:00:00.000Z",
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [2.24028, 48.8075]},
    "properties": {
        "altitude": 76,
        "name": "Meudon",
        "country": "FR",
        "french_department": "92",
        "rain_product_available": 1,
        "timezone": "Europe/Paris",
        "daily_forecast": [
            {"time": "2020-05-20T00:00:00.000Z", "T_min": 12.0, "T_max": 22.0},
        ],
        "forecast": [
            {"time": "2020-05-20T15:00:00.000Z", "T": 18.0},
            {"time": "2020-05-20T16:00:00.000Z", "T": 19.0},
            {"time": "2020-05-20T17:00:00.000Z", "T": 20.0},
        ],
    },
}


def test_forecast_france() -> None:
    """Test weather forecast results from API."""
    client = MeteoFranceClient()

    weather_forecast = client.get_forecast(latitude=48.8075, longitude=2.24028)
    now = datetime.now(timezone.utc)

    assert isinstance(weather_forecast.position, ForecastPosition)
    assert isinstance(weather_forecast.updated_on, int)
    assert isinstance(weather_forecast.daily_forecast[0], DailyForecast)
    assert isinstance(weather_forecast.forecast[0], HourlyForecast)
    assert isinstance(weather_forecast.probability_forecast[0], ProbabilityForecast)
    assert isinstance(
        weather_forecast.iso_to_locale_time(weather_forecast.daily_forecast[0].time),
        datetime,
    )

    nearest = weather_forecast.nearest_forecast
    nearest_time = datetime.fromisoformat(nearest.time.replace("Z", "+00:00"))
    assert abs((nearest_time - now).total_seconds()) <= 30 * 60

    current = weather_forecast.current_forecast
    current_time = datetime.fromisoformat(current.time.replace("Z", "+00:00"))
    assert now - timedelta(hours=1) <= current_time <= now

    assert weather_forecast.today_forecast.time == weather_forecast.daily_forecast[0].time


def test_forecast_world() -> None:
    """Test weather forecast results from API."""
    client = MeteoFranceClient()

    weather_forecast = client.get_forecast(latitude=45.5016889, longitude=73.567256)
    now = datetime.now(timezone.utc)

    assert isinstance(weather_forecast.position, ForecastPosition)
    assert isinstance(weather_forecast.updated_on, int)
    assert isinstance(weather_forecast.daily_forecast[0], DailyForecast)
    assert isinstance(weather_forecast.forecast[0], HourlyForecast)
    assert not weather_forecast.probability_forecast
    assert isinstance(
        weather_forecast.iso_to_locale_time(weather_forecast.daily_forecast[0].time),
        datetime,
    )

    nearest = weather_forecast.nearest_forecast
    nearest_time = datetime.fromisoformat(nearest.time.replace("Z", "+00:00"))
    min_distance = min(
        abs((datetime.fromisoformat(x.time.replace("Z", "+00:00")) - now).total_seconds())
        for x in weather_forecast.forecast
    )
    assert abs((nearest_time - now).total_seconds()) == min_distance

    assert weather_forecast.current_forecast.time == weather_forecast.nearest_forecast.time
    assert weather_forecast.today_forecast.time == weather_forecast.daily_forecast[0].time


def test_forecast_current_fallback(requests_mock: Mock) -> None:
    """Test that current_forecast falls back to nearest when no exact hour match."""
    client = MeteoFranceClient()
    requests_mock.request(
        "get", f"{METEOFRANCE_API_URL}/v2/forecast", json=FORECAST_PAST_RESPONSE
    )
    forecast = client.get_forecast(latitude=48.8075, longitude=2.24028)
    assert forecast.current_forecast == forecast.nearest_forecast


def test_forecast_timestamp_to_locale_time(requests_mock: Mock) -> None:
    """Test conversion of a Unix timestamp to locale datetime on a Forecast."""
    client = MeteoFranceClient()
    requests_mock.request(
        "get", f"{METEOFRANCE_API_URL}/v2/forecast", json=FORECAST_PAST_RESPONSE
    )
    forecast = client.get_forecast(latitude=48.8075, longitude=2.24028)
    dt = forecast.timestamp_to_locale_time(1591279200)
    assert isinstance(dt, datetime)
    assert str(dt) == "2020-06-04 16:00:00+02:00"


def test_forecast_place() -> None:
    """Test weather forecast results from API."""
    client = MeteoFranceClient()

    weather_forecast = client.get_forecast_for_place(place=Place.from_dict(MOUNTAIN_CITY))

    assert isinstance(weather_forecast.position, ForecastPosition)
    assert isinstance(weather_forecast.updated_on, int)
    assert isinstance(weather_forecast.daily_forecast[0], DailyForecast)
    assert isinstance(weather_forecast.forecast[0], HourlyForecast)
    assert isinstance(weather_forecast.probability_forecast[0], ProbabilityForecast)
    assert isinstance(
        weather_forecast.iso_to_locale_time(weather_forecast.daily_forecast[0].time),
        datetime,
    )
