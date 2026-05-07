"""Ephemeris Python model for the Météo-France REST API."""

from dataclasses import dataclass


@dataclass
class Ephemeris:
    """Sun and moon data for a given location and day.

    Attributes:
        sunrise_time: ISO 8601 UTC string of sunrise time.
        sunset_time: ISO 8601 UTC string of sunset time.
        moonrise_time: ISO 8601 UTC string of moonrise time.
        moonset_time: ISO 8601 UTC string of moonset time.
        moon_phase: Moon phase as a float string (0.0–1.0).
        moon_phase_description: Human-readable moon phase name.
        saint: Name of the saint of the day.
    """

    sunrise_time: str | None = None
    sunset_time: str | None = None
    moonrise_time: str | None = None
    moonset_time: str | None = None
    moon_phase: str | None = None
    moon_phase_description: str | None = None
    saint: str | None = None

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "Ephemeris":
        """Build an Ephemeris from a v2/ephemeris API response dict."""
        eph = raw_data.get("properties", {}).get("ephemeris", {})
        return cls(
            sunrise_time=eph.get("sunrise_time"),
            sunset_time=eph.get("sunset_time"),
            moonrise_time=eph.get("moonrise_time"),
            moonset_time=eph.get("moonset_time"),
            moon_phase=eph.get("moon_phase"),
            moon_phase_description=eph.get("moon_phase_description"),
            saint=eph.get("saint"),
        )
