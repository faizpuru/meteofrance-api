"""Dictionary Python model for the Météo-France REST API."""

from dataclasses import dataclass


@dataclass
class PhenomenonDictionaryEntry:
    """A single meteorological phenomenon entry.

    Attributes:
        id: Unique identifier of the phenomenon.
        name: Name of the phenomenon.
    """

    id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "PhenomenonDictionaryEntry":
        """Build a PhenomenonDictionaryEntry from a raw API dict."""
        return cls(id=data["id"], name=data["name"])


@dataclass
class ColorDictionaryEntry:
    """A single color entry used in meteorological warnings.

    Attributes:
        id: Unique identifier of the color.
        level: Severity level associated with the color.
        name: Name of the color.
        hex_code: Hexadecimal color code.
    """

    id: int
    level: int
    name: str
    hex_code: str

    @classmethod
    def from_dict(cls, data: dict) -> "ColorDictionaryEntry":
        """Build a ColorDictionaryEntry from a raw API dict."""
        return cls(
            id=data["id"],
            level=data["level"],
            name=data["name"],
            hex_code=data["hexaCode"],
        )


@dataclass
class WarningDictionary:
    """Météo-France meteorological dictionary.

    Attributes:
        phenomenons: List of meteorological phenomenon entries.
        colors: List of warning color entries.
    """

    phenomenons: list[PhenomenonDictionaryEntry]
    colors: list[ColorDictionaryEntry]

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "WarningDictionary":
        """Build a WarningDictionary from a v3/warning/dictionary API response dict."""
        return cls(
            phenomenons=[
                PhenomenonDictionaryEntry.from_dict(p)
                for p in raw_data.get("phenomenons", [])
            ],
            colors=[
                ColorDictionaryEntry.from_dict(c)
                for c in raw_data.get("colors", [])
            ],
        )

    def get_phenomenon_by_id(self, phenomenon_id: int) -> PhenomenonDictionaryEntry | None:
        """Return the phenomenon with the given ID, or None."""
        return next(
            (p for p in self.phenomenons if p.id == phenomenon_id), None
        )

    def get_phenomenon_name_by_id(self, phenomenon_id: int) -> str | None:
        """Return the name of the phenomenon with the given ID, or None."""
        phenomenon = self.get_phenomenon_by_id(phenomenon_id)
        return phenomenon.name if phenomenon is not None else None

    def get_color_by_id(self, color_id: int) -> ColorDictionaryEntry | None:
        """Return the color with the given ID, or None."""
        return next((c for c in self.colors if c.id == color_id), None)

    def get_color_name_by_id(self, color_id: int) -> str | None:
        """Return the name of the color with the given ID, or None."""
        color = self.get_color_by_id(color_id)
        return color.name if color is not None else None
