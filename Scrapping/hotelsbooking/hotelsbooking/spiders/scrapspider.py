import json
import os
from pathlib import Path

import scrapy

# from ..items import HotelsbookingItem


class BookingSpider(scrapy.Spider):

    project_root = Path(__file__).resolve().parents[4]
    default_cities_file = project_root / "cities_weather.json"
    cities_file = Path(os.getenv("CITIES_WEATHER_PATH", str(default_cities_file)))
    with cities_file.open("r", encoding="utf-8") as f:
        city_payload = json.load(f)
    if isinstance(city_payload, dict):
        cities = list(city_payload.keys())
    else:
        cities = [city for city in city_payload]
    # cities = ["Paris"]
    name = 'spider'
    # REDIRECT_ENABLED = False
    custom_settings = {
        "FEEDS": {"hotels.json": {"format": "json"}},
        # "LOG_LEVEL": logging.ERROR
    }
    start_urls = ['https://www.booking.com/index.fr.html']

    # bouton disabled fc63351294 f9c5690c58
    # //*[@id="search_results_table"]/div[2]/div/div/div/div[5]/div[2]/nav/div/div[3]/button

    def parse(self, response):
        # page = 1
        for city in self.cities:
            # while response.xpath("//*[@id='search_results_table']/div[2]/div/div/div/div[4]/div[2]/nav/div/div[3]/button[not(@disabled)]").get() is not None:
            # NEXT_XPATH = response.xpath("//*/button[@aria-label='Page suivante'][@disabled]")
            # while response.xpath("//*/button[@aria-label='Page suivante'][not(@disabled)]").get()
            # while NEXT_XPATH is not None:
            # for i in range(10):
            #     offset = str(25 * (page + i))
            yield scrapy.FormRequest.from_response(
                response,
                formdata={'ss': city},  # 'offset': offset},
                cb_kwargs={'city': city},
                callback=self.after_search
            )

    def after_search(self, response, city):
        r = response.css('div.a826ba81c4.fe821aea6c.fa2f36ad22.afd256fc79.d08f526e0d.ed11e24d01.ef9845d4b3.da89aeb942')
        for hotel in r:
            yield {
                "city": city,
                "hotel_name": hotel.css('.a23c043802::text').get(),
                "hotel_score": hotel.css('div.b5cd09854e.d10a6220b4::text').get(),
                "hotel_description": hotel.css('.aacd9d0b0a.ef8295f3e6.d8eab2cf7f::text').get(),
                "hotel_url": hotel.css('a::attr(href)').get()
            }
        button_next_disabled = response.xpath("//*/button[@aria-label='Page suivante'][@disabled]").get()
        if button_next_disabled is None:
            url = response.url
            try:
                offset = "&offset=" + str((int(url.split("&offset=")[1]) + 25))
            except IndexError:
                offset = "&offset=25"
            next_url = response.url.split("offset=")[0] + offset
            # except IndexError:
            #     next_url = f"{response.url}&offset=25"
            yield response.follow(next_url,  callback=self.after_search, cb_kwargs={'city': city})
            
            
