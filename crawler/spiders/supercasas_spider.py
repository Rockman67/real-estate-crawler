# -*- coding: utf-8 -*-
"""
SuperCasas spider — JS-detail + anti-rate-limit cleanup (Stage 2.6 final)
"""

import re
from urllib.parse import urljoin

from scrapy import Request

from ..items import RealEstateItem
from .real_estate_spider import RealEstateSpider


class SuperCasasSpider(RealEstateSpider):
    name = "supercasas"
    base_url = "https://www.supercasas.com/buscar/"

    custom_settings = {
        # мягкий троттлинг против 429
        "DOWNLOAD_DELAY": 3,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        # playwright
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    filter_mapping = {
        "beds": "RoomsFrom",
        "baths": "BathsFrom",
        "price_min": "PriceFrom",
        "price_max": "PriceTo",
        "type": "ObjectType",
    }

    # ───────────────────────── list page ──────────────────────────
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

    # ───────────────────────── detail page ─────────────────────────
    def parse_detail(self, response):
        base = response.meta["item"]
        html_text = response.text

        # helpers ---------------------------------------------------
        def grab(keyword: str) -> str:
            sel = response.xpath(
                f"string(//label[b[contains(., '{keyword}')]])"
            ).get(default="")
            if sel:
                return sel
            m = re.search(
                rf"{keyword}[^0-9A-Za-zÀ-ÿ]*([^\n<]+)", html_text, re.I
            )
            return m.group(1) if m else ""

        def clean_condition(text: str) -> str | None:
            # удаляем HTML-теги и мусор после первой точки
            text = re.sub(r"<.*?>", "", text)
            text = text.split(".")[0]
            return text.strip() or None

        # extract ---------------------------------------------------
        base.update(
            {
                "beds": self._number(grab("Habitaciones")),
                "baths": self._number(grab("Baños")),
                "area_m2": self._number(grab("Construcción")),
                "condition": clean_condition(grab("Condición")),
            }
        )

        # validate & yield -----------------------------------------
        try:
            yield RealEstateItem(**base).dict()
        except Exception as exc:
            self.logger.error(f"Validation error: {exc} — {base['url']}")

    # ───────────────────────── utils ──────────────────────────────
    @staticmethod
    def _number(text: str | None):
        if not text:
            return None
        m = re.search(r"\d+(?:\.\d+)?", text.replace(",", "").replace(" ", ""))
        if not m:
            return None
        val = float(m.group())
        return int(val) if val.is_integer() else val
