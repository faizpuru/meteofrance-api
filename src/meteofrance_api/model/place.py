"""Place Python model for the Météo-France REST API."""

from dataclasses import dataclass


@dataclass(repr=False)
class Place:
    """Class to access the results of a `v2/places` API request.

    Attributes:
        name: Name of the place.
        latitude: Latitude in degrees.
        longitude: Longitude in degrees.
        country: Country code (e.g. "FR").
        insee: INSEE ID of the place (France only).
        admin: Administrative area name (e.g. region or département).
        admin2: Administrative code (e.g. département number for France).
        postal_code: ZIP code of the location.
    """

    name: str
    latitude: float
    longitude: float
    country: str
    insee: str | None = None
    admin: str | None = None
    admin2: str | None = None
    postal_code: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Place":
        """Build a Place from a v2/places API response entry."""
        return cls(
            name=data["name"],
            latitude=data["lat"],
            longitude=data["lon"],
            country=data["country"],
            insee=data.get("insee"),
            admin=data.get("admin"),
            admin2=data.get("admin2"),
            postal_code=data.get("postCode"),
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}"
            f"(name={self.name}, country={self.country}, admin={self.admin})>"
        )

    def __str__(self) -> str:
        if self.country == "FR":
            return f"{self.name} - {self.admin} ({self.admin2}) - {self.country}"
        return f"{self.name} - {self.admin} - {self.country}"
