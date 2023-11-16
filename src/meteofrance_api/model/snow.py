# -*- coding: utf-8 -*-
"""Snow data Python model for the Météo-France REST API."""
from typing import List
from typing import Optional
from typing import TypedDict
from typing import Union


class Location(TypedDict):
    """Represents a location with a specific type and value.

    Attributes:
        location_type (str): The type of the location (e.g., 'alti').
        value (str): The value associated with the location type, like a specific altitude.
    """

    location_type: str
    value: str


class AvalancheRiskPerLocation(TypedDict):
    """Details the avalanche risk for a specific location.

    Attributes:
        avalanche_risk (int): The level of avalanche risk.
        risk_evolution (Optional[str]): The evolution of the risk over time, can be None.
        location (Location): The specific location for which the risk is assessed.
    """

    avalanche_risk: int
    risk_evolution: Union[None, str]
    location: Location


class MassifAvalancheRisk(TypedDict):
    """Details the avalanche risk for a specific location.

    Attributes:
        avalanche_risk (int): The level of avalanche risk.
        risk_evolution (Optional[str]): The evolution of the risk over time, can be None.
        location (Location): The specific location for which the risk is assessed.
    """

    description: str
    avalanche_risk_max: int
    time: str
    dangerous_exposition: List[str]
    avalanche_risk_per_location: List[AvalancheRiskPerLocation]


class SnowDepth(TypedDict):
    """Represents the depth of snow at a certain altitude and date.

    Attributes:
        altitude (int): The altitude for which the snow depth is recorded.
        date (str): The date of the snow depth measurement.
        value (int): The depth of snow at the given altitude and date.
    """

    altitude: int
    date: str
    value: int


class FreshSnowPerExposition(TypedDict):
    """Details about the fresh snow depth according to exposition.

    Attributes:
        time (str): The time when the measurements were taken.
        exposition (str): The exposition direction (e.g., 'N', 'S').
        fresh_snow_depth (List[SnowDepth]): List of snow depths at different altitudes.
    """

    time: str
    exposition: str
    fresh_snow_depth: List[SnowDepth]


class TotalSnowPerExposition(TypedDict):
    """Information about the total snow depth according to exposition.

    Attributes:
        time (str): The time when the measurements were taken.
        exposition (str): The exposition direction (e.g., 'N', 'S').
        snow_limit (int): The altitude above which snow is present.
        total_snow_depth (List[SnowDepth]): List of total snow depths at different altitudes.
    """

    time: str
    exposition: str
    snow_limit: int
    total_snow_depth: List[SnowDepth]


class SnowPropertiesData(TypedDict):
    """Represents various properties of a geographic feature.

    Attributes:
        massif_name (str): The name of the massif.
        massif_altitude_min (int): The minimum altitude of the massif.
        massif_altitude_max (int): The maximum altitude of the massif.
        massif_avalanche_risk (MassifAvalancheRisk): Avalanche risk information for the massif.
        fresh_snow_per_exposition (List[FreshSnowPerExposition]): Information on fresh snow
            according to exposition.
        total_snow_per_exposition (List[TotalSnowPerExposition]): Information on total snow depth
            according to exposition.
    """

    massif_name: str
    massif_altitude_min: int
    massif_altitude_max: int
    massif_avalanche_risk: MassifAvalancheRisk
    fresh_snow_per_exposition: List[FreshSnowPerExposition]
    avalanche_report: str
    total_snow_per_exposition: List[TotalSnowPerExposition]


class SnowData(TypedDict):
    """A complete representation of snow data for a massif, including its type, update time, and properties.

    Attributes:
        type (str): The type of the data, usually indicating the nature of the data representation.
        update_time (str): The timestamp indicating the last update time of the snow data.
        properties (SnowPropertiesData): Detailed properties of the snow data,
            including information about the massif, avalanche risks, and snow depth.
    """

    type: str
    update_time: str
    properties: SnowPropertiesData


class Snow:
    """Class representing snow data for a massif, encapsulating the Feature TypedDict.

    Attributes:
        raw_data (SnowData): The SnowData object containing snow data. It holds all
                                the relevant information about the snow conditions,
                                avalanche risks, and other properties related to the
                                massif.
    """

    def __init__(self, raw_data: SnowData):
        """Initializes the Snow object with data from a SnowData object.

        Args:
            raw_data (SnowData): The SnowData object containing snow data.
        """
        self.raw_data = raw_data

    def get_massif_name(self) -> str:
        """Returns the name of the massif.

        Returns:
            The name of the massif as a string.
        """
        return self.raw_data["properties"]["massif_name"]

    def get_max_avalanche_risk(self) -> int:
        """Returns the maximum avalanche risk level for the massif.

        Returns:
            The maximum avalanche risk level as an integer.
        """
        return self.raw_data["properties"]["massif_avalanche_risk"][
            "avalanche_risk_max"
        ]

    def get_snow_depth_at_altitude(self, altitude: int) -> Optional[int]:
        """Returns the snow depth at a specified altitude, if available.

        Args:
            altitude (int): The altitude for which to get the snow depth.

        Returns:
            The snow depth at the specified altitude as an integer, or None if not available.
        """
        for snow_depth_info in self.raw_data["properties"]["total_snow_per_exposition"]:
            for depth in snow_depth_info["total_snow_depth"]:
                if depth["altitude"] == altitude:
                    return depth["value"]
        return None

    def get_available_altitudes(self) -> List[int]:
        """Returns a list of unique altitudes where snow depth measurements are available.

        Returns:
            A list of integers representing the available altitudes.
        """
        altitudes = set()
        for exposition in self.raw_data["properties"]["total_snow_per_exposition"]:
            for depth_info in exposition["total_snow_depth"]:
                altitudes.add(depth_info["altitude"])

        return sorted(altitudes)

    def get_avalanche_risk_by_location_value(
        self, location_value: str
    ) -> Optional[int]:
        """Returns the avalanche risk for a specific location value.

        Args:
            location_value (str): The value associated with the location type (e.g., '< 2200').

        Returns:
            The avalanche risk level as an integer, or None if not available for the given location value.
        """
        risks = self.raw_data["properties"]["massif_avalanche_risk"][
            "avalanche_risk_per_location"
        ]
        for risk in risks:
            if risk["location"]["value"] == location_value:
                return risk["avalanche_risk"]

        return None

    def get_snow_depths(self) -> List[dict]:
        """Generates a list of snow depths by exposition and altitude.

        Returns:
            A list of dictionaries, each containing the exposition, altitude, and corresponding snow depth.
        """
        snow_depth_list = []

        # For total snow depth
        for exposition_data in self.raw_data["properties"]["total_snow_per_exposition"]:
            exposition = exposition_data["exposition"]
            for depth_data in exposition_data["total_snow_depth"]:
                snow_depth_list.append(
                    {
                        "exposition": exposition,
                        "altitude": depth_data["altitude"],
                        "total_snow_depth": depth_data["value"],
                    }
                )

        return snow_depth_list

    def get_snow_limits(self) -> dict:
        """Retrieves the snow limit altitude for each exposition.

        Returns:
            A dictionary where keys are expositions (e.g., 'N', 'S')
                and values are the corresponding snow limit altitudes.
        """
        snow_limits = {}

        for exposition_data in self.raw_data["properties"]["total_snow_per_exposition"]:
            exposition = exposition_data["exposition"]
            snow_limit = exposition_data["snow_limit"]

            snow_limits[exposition] = snow_limit

        return snow_limits

    def get_avalanche_risks(self) -> dict:
        """Returns all avalanche risks organized by location value.

        Returns:
            A dictionary with location values as keys and avalanche risks as values.
        """
        risks_map = {}
        risks = self.raw_data["properties"]["massif_avalanche_risk"][
            "avalanche_risk_per_location"
        ]
        for risk in risks:
            location_value = risk["location"]["value"]
            risks_map[location_value] = risk["avalanche_risk"]

        return risks_map

    def get_fresh_snow(self) -> dict:
        """Returns fresh snow depth data organized by date, altitude, and exposition.

        Returns:
            A nested dictionary where keys are dates,
                mapping to dictionaries of (altitude, exposition) keys and snow depths as values.
        """
        fresh_snow_map = {}
        fresh_snow_data = self.raw_data["properties"]["fresh_snow_per_exposition"]

        for exposition_data in fresh_snow_data:
            exposition = exposition_data["exposition"]

            for snow_depth in exposition_data["fresh_snow_depth"]:
                date = snow_depth["date"]
                altitude = snow_depth["altitude"]
                value = snow_depth["value"]

                if date not in fresh_snow_map:
                    fresh_snow_map[date] = {}

                fresh_snow_map[date][(altitude, exposition)] = value

        return fresh_snow_map
