"""Weather alert bulletin Python model for the Météo-France REST API.

For getting weather alerts in metropolitan France and Andorre.
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class PhenomenonMaxColor:
    """A meteorological phenomenon and its maximum alert color code.

    Attributes:
        phenomenon_id: Unique identifier for the meteorological phenomenon.
        phenomenon_max_color_id: Maximum alert color code (1=green, 2=yellow, 3=orange, 4=red).
    """

    phenomenon_id: str
    phenomenon_max_color_id: int

    @classmethod
    def from_dict(cls, data: dict) -> "PhenomenonMaxColor":
        """Build a PhenomenonMaxColor from a raw API dict."""
        return cls(
            phenomenon_id=data["phenomenon_id"],
            phenomenon_max_color_id=data["phenomenon_max_color_id"],
        )


@dataclass
class CurrentPhenomenons:
    """Class to access the results of a `warning/currentPhenomenons` REST API request.

    For coastal department two bulletins are available corresponding to two different
    domains.

    Attributes:
        update_time: Timestamp of the latest update of the phenomenons.
        end_validity_time: Timestamp of the expiration date of the phenomenons.
        domain_id: Domain ID of the bulletin ('France' or a department number).
        phenomenons_max_colors: List of phenomenons with their current alert level.
    """

    update_time: int
    end_validity_time: int
    domain_id: str
    phenomenons_max_colors: list[PhenomenonMaxColor] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "CurrentPhenomenons":
        """Build a CurrentPhenomenons from a v3/warning/currentphenomenons API response."""
        return cls(
            update_time=raw_data["update_time"],
            end_validity_time=raw_data["end_validity_time"],
            domain_id=raw_data["domain_id"],
            phenomenons_max_colors=[
                PhenomenonMaxColor.from_dict(p)
                for p in raw_data.get("phenomenons_max_colors", [])
            ],
        )

    def merge_with_coastal_phenomenons(
        self, coastal_phenomenons: "CurrentPhenomenons"
    ) -> None:
        """Merge the classical phenomenons bulletin with the coastal one."""
        self.phenomenons_max_colors.extend(coastal_phenomenons.phenomenons_max_colors)

    def get_domain_max_color(self) -> int:
        """Return the maximum alert level across all phenomenons in the domain."""
        return max(x.phenomenon_max_color_id for x in self.phenomenons_max_colors)


@dataclass
class Full:
    """Class to access the results of a `warning/full` REST API request.

    For a given domain we can access the maximum alert, a timelaps of the alert
    evolution for the next 24 hours, and a list of alerts.

    Attributes:
        update_time: Timestamp of the latest update.
        end_validity_time: Timestamp of the expiration date.
        domain_id: Domain ID ('France' or a department number).
        color_max: Maximum alert level in the domain.
        timelaps: Schedule of each phenomenon for the next 24 hours.
        phenomenons_items: Alert level for each phenomenon type.
    """

    update_time: int
    end_validity_time: int
    domain_id: str
    color_max: int
    timelaps: list[dict[str, Any]] = field(default_factory=list)
    phenomenons_items: list[PhenomenonMaxColor] = field(default_factory=list)

    @classmethod
    def from_api_response(cls, raw_data: dict) -> "Full":
        """Build a Full from a v3/warning/full API response."""
        return cls(
            update_time=raw_data["update_time"],
            end_validity_time=raw_data["end_validity_time"],
            domain_id=raw_data["domain_id"],
            color_max=raw_data["color_max"],
            timelaps=raw_data.get("timelaps", []),
            phenomenons_items=[
                PhenomenonMaxColor.from_dict(p)
                for p in raw_data.get("phenomenons_items", [])
            ],
        )

    def merge_with_coastal_phenomenons(self, coastal_phenomenons: "Full") -> None:
        """Merge the classical phenomenon bulletin with the coastal one."""
        self.color_max = max(self.color_max, coastal_phenomenons.color_max)
        self.timelaps.extend(coastal_phenomenons.timelaps)
        self.phenomenons_items.extend(coastal_phenomenons.phenomenons_items)
