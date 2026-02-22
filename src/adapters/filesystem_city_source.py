import json
from collections.abc import Sequence
from pathlib import Path


class JsonCitySource:
    def __init__(self, city_weather_path: str) -> None:
        self._path = Path(city_weather_path)

    def list_cities(self) -> Sequence[str]:
        with self._path.open("r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)
        if isinstance(payload, dict):
            return list(payload.keys())
        if isinstance(payload, list):
            return [str(item) for item in payload]
        raise ValueError("Unsupported city weather payload format")
