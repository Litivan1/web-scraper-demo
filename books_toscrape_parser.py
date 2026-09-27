"""
Example implementation of BaseParser for https://books.toscrape.com —
a public sandbox site made specifically for scraping practice.

This shows the pattern used for real e-commerce/catalog scraping projects:
a small reusable base class + one concrete parser per source site, each
translating that site's markup into a common ParsedProduct shape so the
rest of a pipeline (dedup, storage, sync) never has to care which site
a product came from.
"""
import re
from urllib.parse import urljoin

from base import BaseParser, ParsedProduct, ParsedVariant

STOCK_RE = re.compile(r"(\d+)\s+available")


class BooksToScrapeParser(BaseParser):

    def parse_catalog(self, catalog_url: str) -> list[str]:
        soup = self.soup(catalog_url)
        links = []
        for a in soup.select("article.product_pod h3 a"):
            href = a.get("href", "")
            links.append(urljoin(catalog_url, href))
        return links

    def parse_product(self, url: str) -> ParsedProduct | None:
        try:
            soup = self.soup(url)
        except Exception:
            return None

        title_el = soup.select_one("div.product_main h1")
        if not title_el:
            return None

        price_el = soup.select_one("p.price_color")
        price = None
        if price_el:
            digits = "".join(c for c in price_el.get_text() if c.isdigit() or c == ".")
            price = float(digits) if digits else None

        availability_el = soup.select_one("p.availability")
        stock = 0
        if availability_el:
            match = STOCK_RE.search(availability_el.get_text())
            stock = int(match.group(1)) if match else 0

        description_el = soup.select_one("#product_description ~ p")
        description = description_el.get_text(strip=True) if description_el else ""

        image_el = soup.select_one("div.item.active img")
        image_urls = [urljoin(url, image_el["src"])] if image_el else []

        rating_el = soup.select_one("p.star-rating")
        rating = rating_el.get("class", [""])[-1] if rating_el else ""

        return ParsedProduct(
            source_url=url,
            source_product_id=url.rstrip("/").split("/")[-2],
            title=title_el.get_text(strip=True),
            description=description,
            price=price,
            image_urls=image_urls,
            variants=[ParsedVariant(stock=stock, price=price, source_id="default")],
            attributes={"rating": rating},
        )
