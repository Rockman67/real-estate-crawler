# -*- coding: utf-8 -*-
"""
SuperCasas spider — list + detail (Stage 2.6 fixed selectors)
"""

import re
from urllib.parse import urljoin

from scrapy import Request

from ..items import RealEstateItem
from .real_estate_spider import RealEstateSpider


class SuperCasasSpider(RealEstateSpider):
    name = "supercasas"
    base_url = "https://www.supercasas.com/buscar/"

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
            yield Request(item["url"], callback=self.parse_detail, meta={"item": item})

    # ───────────────────────── detail page ─────────────────────────
    def parse_detail(self, response):
        base = response.meta["item"]

        # helpers ---------------------------------------------------
        def grab(keyword: str) -> str:
            """
            Return full text of <label><b>keyword</b>: value</label>
            using XPath string() to get inside-tag text.
            """
            path = f"string(//label[b[contains(., '{keyword}')]])"
            return response.xpath(path).get(default="").strip()

        # update fields --------------------------------------------
        base.update(
            {
                "beds": self._number(grab("Habitaciones")),
                "baths": self._number(grab("Baños")),
                "area_m2": self._number(grab("Construcción")),
                "condition": grab("Condición").split(":")[-1].strip() or None,
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
        """
        Extract first int/float from string, return as int if整数 иначе float.
        """
        if not text:
            return None
        m = re.search(r"\d+(?:\.\d+)?", text.replace(",", "").replace(" ", ""))
        if not m:
            return None
        num = float(m.group())
        return int(num) if num.is_integer() else num
