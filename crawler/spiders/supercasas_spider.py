# -*- coding: utf-8 -*-
"""
SuperCasas spider — list + JS-detail (final selectors)
"""

import re
from urllib.parse import urljoin

from scrapy import Request

from ..items import RealEstateItem
from .real_estate_spider import RealEstateSpider


class SuperCasasSpider(RealEstateSpider):
    name = "supercasas"
    base_url = "https://www.supercasas.com/buscar/"

    # ───────────── throttling vs 429 ─────────────
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2,
        "AUTOTHROTTLE_MAX_DELAY": 10,
    }

    filter_mapping = {
        "beds": "RoomsFrom",
        "baths": "BathsFrom",
        "price_min": "PriceFrom",
        "price_max": "PriceTo",
        "type": "ObjectType",
    }

    # ───────────────── list page ─────────────────
    def parse_list(self, response):
        for li in response.css("#bigsearch-results-inner-results li"):
            href = li.css("a::attr(href)").get()
            if not href:
                continue
            item = {
                "url": urljoin(response.url, href),
                "title": li.css(".title1::text").get("").strip(),
                "price_raw": li.css(".title2::text").get("").strip(),
                "price": self._number(li.css(".title2::text").get("")),
                "location_raw": li.css(".type::text").get("").strip(),
            }
            yield Request(
                item["url"],
                callback=self.parse_detail,
                meta={"item": item, "playwright": True},
            )

    # ──────────────── detail page ───────────────
    def parse_detail(self, response):
        base = response.meta["item"]

        # helper: text after ":" in a label
        def after_colon(keyword: str) -> str:
            sel = response.xpath(
                f"//label[b[contains(., '{keyword}')]]/text()"
            ).get(default="")
            return sel.strip()

        # helper: numeric
        def num(text: str | None):
            m = re.search(r"\d+(?:\.\d+)?", text or "")
            if not m:
                return None
            val = float(m.group())
            return int(val) if val.is_integer() else val

        # condition cleaner
        def clean_cond(text: str):
            text = re.sub(r"<.*?>", "", text)
            text = text.split(".")[0].strip()
            return text or None

        base.update(
            {
                "beds": num(after_colon("Habitaciones")),
                "baths": num(after_colon("Baños")),
                "area_m2": num(after_colon("Construcción")),
                "condition": clean_cond(after_colon("Condición")),
            }
        )

        try:
            yield RealEstateItem(**base).dict()
        except Exception as exc:
            self.logger.error(f"Validation error: {exc} — {base['url']}")

    # ────────────────── utils ────────────────────
    @staticmethod
    def _number(text: str | None):
        m = re.search(r"\d+(?:\.\d+)?", (text or "").replace(",", ""))
        if not m:
            return None
        val = float(m.group())
        return int(val) if val.is_integer() else val
