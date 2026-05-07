"""Picture of the Day Python model for the Météo-France REST API."""

from dataclasses import dataclass


@dataclass
class PictureOfTheDay:
    """Class to access the results of a `v2/report` REST API request.

    Attributes:
        image_url: URL of the picture of the day (JPG).
        description: Description of the picture of the day.
    """

    image_url: str
    description: str
