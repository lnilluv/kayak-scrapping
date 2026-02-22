from __future__ import annotations

from collections.abc import Sequence

import scrapy
from scrapy.crawler import CrawlerProcess


class _BookingSpider(scrapy.Spider):
    name = "booking_spider"
    start_urls = ["https://www.booking.com/index.fr.html"]

    def __init__(self, cities: Sequence[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cities = list(cities)

    def parse(self, response):
        for city in self.cities:
            yield scrapy.FormRequest.from_response(
                response,
                formdata={"ss": city},
                cb_kwargs={"city": city},
                callback=self.after_search,
            )

    def after_search(self, response, city):
        hotels = response.css(
            "div.a826ba81c4.fe821aea6c.fa2f36ad22.afd256fc79.d08f526e0d.ed11e24d01.ef9845d4b3.da89aeb942"
        )
        for hotel in hotels:
            yield {
                "city": city,
                "hotel_name": hotel.css(".a23c043802::text").get(),
                "hotel_score": hotel.css("div.b5cd09854e.d10a6220b4::text").get(),
                "hotel_description": hotel.css(
                    ".aacd9d0b0a.ef8295f3e6.d8eab2cf7f::text"
                ).get(),
                "hotel_url": hotel.css("a::attr(href)").get(),
            }

        button_next_disabled = response.xpath(
            "//*/button[@aria-label='Page suivante'][@disabled]"
        ).get()
        if button_next_disabled is None:
            url = response.url
            try:
                offset = "&offset=" + str((int(url.split("&offset=")[1]) + 25))
            except IndexError:
                offset = "&offset=25"
            next_url = response.url.split("offset=")[0] + offset
            yield response.follow(
                next_url, callback=self.after_search, cb_kwargs={"city": city}
            )


class ScrapyBookingAdapter:
    def scrape(self, cities: Sequence[str], output_path: str) -> None:
        process = CrawlerProcess(
            settings={
                "FEEDS": {output_path: {"format": "json"}},
                "ROBOTSTXT_OBEY": False,
                "AUTOTHROTTLE_ENABLED": True,
                "AUTOTHROTTLE_START_DELAY": 2,
                "AUTOTHROTTLE_MAX_DELAY": 20,
                "DOWNLOADER_MIDDLEWARES": {
                    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
                    "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
                },
                "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
                "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
                "LOG_LEVEL": "INFO",
            }
        )
        process.crawl(_BookingSpider, cities=list(cities))
        process.start()
