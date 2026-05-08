"""Rain in the next hour Python model for the Météo-France REST API."""
# pylint: disable=duplicate-code

from dataclasses import dataclass
from dataclasses import fields as dc_fields
from datetime import datetime

from pytz import timezone as pytz_timezone

from meteofrance_api.helpers import timestamp_to_datetime_with_locale_tz


@dataclass
class RainPosition:  # pylint: disable=too-many-instance-attributes
    """Metadata about the rain forecast location."""

    altitude: int | None = None
    name: str | None = None
    country: str | None = None
    french_department: str | None = None
    rain_product_available: int | None = None
    timezone: str | None = None
    lat: float | None = None
    lon: float | None = None

    @classmethod
    def from_api_response(cls, properties: dict, coords: list) -> "RainPosition":
        """Build a RainPosition from a v3/rain API response properties dict."""
        known = {f.name for f in dc_fields(cls)}
        data = {k: v for k, v in properties.items() if k in known}
        data["lat"] = coords[1]
        data["lon"] = coords[0]
        return cls(**data)


@dataclass
class RainForecastEntry:
    """One time-step of rain forecast data."""

    time: str
    rain_intensity: int | None = None
    rain_intensity_description: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "RainForecastEntry":
        """Build a RainForecastEntry from a raw API dict."""
        known = {f.name for f in dc_fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Rain:
    """Class to access the results of a `v2/rain` API request.

    Attributes:
        position: Metadata about the rain forecast location.
        updated_on: Unix timestamp of the latest update.
        forecast: List of rain forecast entries for the next hour.
        confidence: Quality indicator of the rain forecast.
    """

    position: RainPosition
    updated_on: int
    forecast: list[RainForecastEntry]
    confidence: int

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "Rain":
        """Build a Rain from a v2/rain API response dict."""
        if "properties" not in raw_data:
            raise ValueError("Rain forecast not available for this location.")
        properties = raw_data["properties"]
        coords = raw_data["geometry"]["coordinates"]
        dt = datetime.fromisoformat(raw_data["update_time"].replace("Z", "+00:00"))
        return cls(
            position=RainPosition.from_api_response(properties, coords),
            updated_on=int(dt.timestamp()),
            forecast=[RainForecastEntry.from_dict(e) for e in properties["forecast"]],
            confidence=properties.get("confidence", 0),
        )

    def next_rain_date_locale(self) -> datetime | None:
        """Estimate the date of the next rain in the location timezone.

        Returns:
            A datetime of the next rain within the next hour, or None if no rain
            is expected.
        """
        next_rain = next(
            (entry for entry in self.forecast if (entry.rain_intensity or 0) > 1),
            None,
        )
        if next_rain is None:
            return None
        return self.iso_to_locale_time(next_rain.time)

    def timestamp_to_locale_time(self, timestamp: int) -> datetime:
        """Convert a Unix timestamp to a datetime in the rain forecast location timezone."""
        return timestamp_to_datetime_with_locale_tz(timestamp, self.position.timezone)

    def iso_to_locale_time(self, iso_string: str) -> datetime:
        """Convert an ISO 8601 string to a datetime in the rain forecast location timezone."""
        dt_utc = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt_utc.astimezone(pytz_timezone(self.position.timezone))
