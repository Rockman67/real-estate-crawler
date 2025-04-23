# -*- coding: utf-8 -*-
"""
SuperCasas spider — list + JS-rendered detail (Playwright) — Stage 2.6 fix
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
            yield Request(
                item["url"],
                callback=self.parse_detail,
                meta={"item": item, "playwright": True},   # ← JS-рендер обязателен
            )

    # ───────────────────────── detail page ─────────────────────────
    def parse_detail(self, response):
        base = response.meta["item"]
        html_text = response.text

        # helpers ---------------------------------------------------
        def number(text: str | None):
            if not text:
                return None
            m = re.search(r"\d+(?:\.\d+)?", text.replace(",", ""))
            if not m:
                return None
            val = float(m.group())
            return int(val) if val.is_integer() else val

        def get_by_label(keyword: str):
            sel = response.xpath(f"string(//label[b[contains(., '{keyword}')]])").get().strip()
            if sel:
                return sel
            # fallback: regex anywhere in HTML
            m = re.search(rf"{keyword}[^0-9]*([0-9]+(?:\.[0-9]+)?)", html_text, re.I)
            return m.group(0) if m else ""

        # extract ---------------------------------------------------
        base.update(
            {
                "beds": number(get_by_label("Habitaciones")),
                "baths": number(get_by_label("Baños")),
                "area_m2": number(get_by_label("Construcción")),
                "condition": get_by_label("Condición").split(":")[-1].strip() or None,
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
