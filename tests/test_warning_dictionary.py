"""Tests for WarningDictionary class in the Météo-France module."""

import pytest

from meteofrance_api import MeteoFranceClient
from meteofrance_api.model import WarningDictionary
from meteofrance_api.model.dictionary import ColorDictionaryEntry
from meteofrance_api.model.dictionary import PhenomenonDictionaryEntry


SAMPLE_DATA = {
    "phenomenons": [
        {"id": 1, "name": "Wind"},
        {"id": 2, "name": "Rain-flood"},
        {"id": 3, "name": "Thunderstorms"},
        {"id": 4, "name": "Flood"},
        {"id": 5, "name": "Snow-ice"},
        {"id": 6, "name": "Heat wave"},
        {"id": 7, "name": "Extreme Cold"},
        {"id": 8, "name": "Avalanche"},
        {"id": 9, "name": "Waves-flooding"},
    ],
    "colors": [
        {"id": 1, "level": 1, "name": "green", "hexaCode": "#31aa35"},
        {"id": 2, "level": 2, "name": "yellow", "hexaCode": "#fff600"},
        {"id": 3, "level": 3, "name": "orange", "hexaCode": "#ffb82b"},
        {"id": 4, "level": 4, "name": "red", "hexaCode": "#CC0000"},
    ],
}


class TestWarningDictionary:
    """Tests for WarningDictionary class in the Météo-France module."""

    @pytest.fixture
    def dictionary(self) -> WarningDictionary:
        return WarningDictionary.from_api_response(SAMPLE_DATA)

    def test_dictionary(self) -> None:
        """Test dictionary."""
        client = MeteoFranceClient()

        dictionary = client.get_warning_dictionary()

        assert isinstance(dictionary, WarningDictionary)
        assert isinstance(dictionary.get_color_name_by_id(1), str)
        assert isinstance(dictionary.get_phenomenon_name_by_id(1), str)

    def test_get_phenomenon_by_id(self, dictionary: WarningDictionary) -> None:
        """Test get_phenomenon_by_id method."""
        assert dictionary.get_phenomenon_by_id(1) == PhenomenonDictionaryEntry(id=1, name="Wind")
        assert dictionary.get_phenomenon_by_id(99) is None

    def test_get_phenomenon_name_by_id(self, dictionary: WarningDictionary) -> None:
        """Test get_phenomenon_name_by_id method."""
        assert dictionary.get_phenomenon_name_by_id(2) == "Rain-flood"
        assert dictionary.get_phenomenon_name_by_id(99) is None

    def test_get_color_by_id(self, dictionary: WarningDictionary) -> None:
        """Test get_color_by_id method."""
        assert dictionary.get_color_by_id(2) == ColorDictionaryEntry(
            id=2, level=2, name="yellow", hex_code="#fff600"
        )
        assert dictionary.get_color_by_id(99) is None

    def test_get_color_name_by_id(self, dictionary: WarningDictionary) -> None:
        """Test get_color_name_by_id method."""
        assert dictionary.get_color_name_by_id(1) == "green"
        assert dictionary.get_color_name_by_id(99) is None
