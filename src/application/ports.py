from collections.abc import Sequence
from typing import Protocol


class CitySourcePort(Protocol):
    def list_cities(self) -> Sequence[str]:
        ...


class HotelScraperPort(Protocol):
    def scrape(self, cities: Sequence[str], output_path: str) -> None:
        ...
