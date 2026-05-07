"""Météo-France models for the REST API."""

from .dictionary import WarningDictionary
from .ephemeris import Ephemeris
from .forecast import Forecast
from .observation import Observation
from .picture_of_the_day import PictureOfTheDay
from .place import Place
from .rain import Rain
from .warning import CurrentPhenomenons
from .warning import Full
from .warning import PhenomenonMaxColor

__all__ = [
    "Ephemeris",
    "Forecast",
    "Observation",
    "Place",
    "PictureOfTheDay",
    "Rain",
    "CurrentPhenomenons",
    "Full",
    "PhenomenonMaxColor",
    "WarningDictionary",
]
