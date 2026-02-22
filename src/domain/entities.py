from dataclasses import dataclass


@dataclass(frozen=True)
class HotelRecord:
    city: str
    hotel_name: str | None
    hotel_score: str | None
    hotel_description: str | None
    hotel_url: str | None
