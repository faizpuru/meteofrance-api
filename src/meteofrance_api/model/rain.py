# -*- coding: utf-8 -*-
"""Rain Python model for the Météo-France REST API."""
from datetime import datetime
from typing import List
from typing import Optional
from typing import TypedDict

from meteofrance_api.helpers import timestamp_to_dateime_with_locale_tz


class Geometry(TypedDict):
    """Classe pour représenter les données géométriques."""

    type: str
    coordinates: List[float]


class ForecastData(TypedDict):
    """Describing the data structure of forecast object in the rain data."""

    time: int
    rain_intensity: int
    rain_intensity_description: str


class RainPropertiesData(TypedDict):
    """Describing the data structure of properties object in the rain data."""

    altitude: int
    name: str
    country: str
    french_department: str
    rain_product_available: int
    timezone: str
    confidence: int
    forecast: List[ForecastData]


class RainData(TypedDict):
    """Describing the data structure of rain object returned by the REST API."""

    update_time: int
    type: str
    geometry: Geometry
    properties: RainPropertiesData


class Rain:
    """Class to access the results of 'rain' REST API request.

    Attributes are based on the RainData structure.
    """

    def __init__(self, raw_data: RainData) -> None:
        """Initialize a Rain object.

        Args:
            raw_data: A dictionary representing the JSON response from 'rain' REST API
                request. The structure is described by the RainData class.
        """
        self.raw_data = raw_data

    @property
    def update_time(self) -> datetime:
        """Return the update time of the rain data as a datetime object."""
        return self.timestamp_to_locale_time(self.raw_data["update_time"])

    @property
    def geometry(self) -> Geometry:
        """Return the coordinates of the location."""
        return self.raw_data["geometry"]

    @property
    def altitude(self) -> int:
        """Return the altitude of the location."""
        return self.raw_data["properties"]["altitude"]

    @property
    def location_name(self) -> str:
        """Return the name of the location."""
        return self.raw_data["properties"]["name"]

    @property
    def country(self) -> str:
        """Return the country code of the location."""
        return self.raw_data["properties"]["country"]

    @property
    def french_department(self) -> str:
        """Return the French department code of the location."""
        return self.raw_data["properties"]["french_department"]

    @property
    def rain_product_available(self) -> int:
        """Return the availability status of the rain product."""
        return self.raw_data["properties"]["rain_product_available"]

    @property
    def timezone(self) -> str:
        """Return the timezone of the location."""
        return self.raw_data["properties"]["timezone"]

    @property
    def confidence(self) -> int:
        """Return the confidence level of the rain data."""
        return self.raw_data["properties"]["confidence"]

    @property
    def forecasts(self) -> List[ForecastData]:
        """Return the list of forecasts."""
        return self.raw_data["properties"]["forecast"]

    def timestamp_to_locale_time(self, timestamp: int) -> datetime:
        """Convert timestamp in datetime with rain forecast location timezone (Helper).

        Args:
            timestamp: An integer representing the UNIX timestamp.

        Returns:
            A datetime instance corresponding to the timestamp with the timezone of the
                rain forecast location.
        """
        return timestamp_to_dateime_with_locale_tz(timestamp, self.timezone)

    def next_rain_date_locale(self) -> Optional[datetime]:
        """Return the datetime of the next rain.

        Iterates through the forecasts to find the first occurrence of rain.

        Returns:
            A datetime instance representing the time of the next rain, or None if no
            rain is forecasted in the available data.
        """
        for forecast in self.forecasts:
            # Convertir le temps de la prévision en datetime avec le fuseau horaire local
            forecast_time = self.timestamp_to_locale_time(int(forecast["time"]))

            # Vérifier si l'intensité de la pluie indique de la pluie
            if forecast["rain_intensity"] > 1:
                return forecast_time

        return None
