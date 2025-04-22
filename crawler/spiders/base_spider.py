from scrapy import Spider


class BaseSpider(Spider):
    custom_settings = {
        # 30 с таймаут Playwright
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30_000,
    }
