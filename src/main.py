from __future__ import annotations

import argparse
import os
from pathlib import Path

from src.adapters.filesystem_city_source import JsonCitySource
from src.adapters.scrapy_booking_adapter import ScrapyBookingAdapter
from src.application.use_cases import ScrapeHotelsUseCase


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Booking scraper production entrypoint")
    parser.add_argument(
        "--cities-file",
        default=os.getenv("CITIES_WEATHER_PATH", str(_project_root() / "cities_weather.json")),
        help="Path to the cities weather json file",
    )
    parser.add_argument(
        "--output-file",
        default=os.getenv("HOTELS_OUTPUT_PATH", str(_project_root() / "hotels.json")),
        help="Path to output hotels json file",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run wiring/config smoke test without external scraping",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    city_source = JsonCitySource(args.cities_file)
    cities = list(city_source.list_cities())
    if args.smoke:
        print(f"Smoke OK - loaded {len(cities)} cities")
        return

    use_case = ScrapeHotelsUseCase(
        city_source=city_source,
        hotel_scraper=ScrapyBookingAdapter(),
    )
    total = use_case.execute(output_path=args.output_file)
    print(f"Scraping started for {total} cities. Output: {args.output_file}")


if __name__ == "__main__":
    main()
