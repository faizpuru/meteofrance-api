"""Weather observation Python model for the Météo-France REST API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(repr=False)
class Observation:
    """Class to access the results of a `v2/observation` API request.

    Attributes:
        timezone: The observation timezone.
        time_as_string: ISO 8601 string of the observation time.
        temperature: Observed temperature (°C).
        wind_speed: Observed wind speed (km/h).
        wind_direction: Observed wind direction (°).
        wind_icon: Icon ID illustrating the observed wind direction.
        weather_icon: Icon ID illustrating the observed weather condition.
        weather_description: Description of the observed weather condition.
    """

    timezone: str | None = None
    time_as_string: str | None = None
    temperature: float | None = None
    wind_speed: float | None = None
    wind_direction: int | None = None
    wind_icon: str | None = None
    weather_icon: str | None = None
    weather_description: str | None = None

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "Observation":
        """Build an Observation from a v2/observation API response dict."""
        properties = raw_data.get("properties", {})
        gridded = properties.get("gridded", {})
        return cls(
            timezone=properties.get("timezone"),
            time_as_string=gridded.get("time"),
            temperature=gridded.get("T"),
            wind_speed=gridded.get("wind_speed"),
            wind_direction=gridded.get("wind_direction"),
            wind_icon=gridded.get("wind_icon"),
            weather_icon=gridded.get("weather_icon"),
            weather_description=gridded.get("weather_description"),
        )

    @property
    def time_as_datetime(self) -> datetime | None:
        """Return the observation time as a timezone-aware datetime."""
        if self.time_as_string is None:
            return None
        return datetime.strptime(self.time_as_string, "%Y-%m-%dT%H:%M:%S.%f%z")

    def __repr__(self) -> str:
        return (
            f"Observation("
            f"timezone={self.timezone}, "
            f"time={self.time_as_string}, "
            f"temperature={self.temperature}°C, "
            f"wind_speed={self.wind_speed} km/h, "
            f"wind_direction={self.wind_direction}°, "
            f"wind_icon={self.wind_icon}, "
            f"weather_icon={self.weather_icon}, "
            f"weather_description={self.weather_description}"
            ")"
        )
