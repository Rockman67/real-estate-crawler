BOT_NAME = "real_estate_crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEEDS = {"test.json": {"format": "json", "overwrite": True}}
