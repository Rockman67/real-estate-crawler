BOT_NAME = "real_estate_crawler"

SPIDER_MODULES = ["crawler.spiders"]
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
NEWSPIDER_MODULE = "crawler.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
FEEDS = {"test.json": {"format": "json", "overwrite": True}}
