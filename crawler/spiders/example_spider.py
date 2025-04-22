import scrapy
from crawler.spiders.base_spider import BaseSpider


class ExampleSpider(BaseSpider):
    name = "example"
    start_urls = ["https://httpbin.org/html"]

    def parse(self, response):
        yield {"title": response.css("h1::text").get()}
