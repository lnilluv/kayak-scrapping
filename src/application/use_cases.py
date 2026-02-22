from .ports import CitySourcePort, HotelScraperPort


class ScrapeHotelsUseCase:
    def __init__(self, city_source: CitySourcePort, hotel_scraper: HotelScraperPort) -> None:
        self._city_source = city_source
        self._hotel_scraper = hotel_scraper

    def execute(self, output_path: str) -> int:
        cities = list(self._city_source.list_cities())
        if not cities:
            raise ValueError("No cities available to scrape")
        self._hotel_scraper.scrape(cities=cities, output_path=output_path)
        return len(cities)
