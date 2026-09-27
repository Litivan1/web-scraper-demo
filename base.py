from dataclasses import dataclass, field
from typing import Optional
import httpx
from bs4 import BeautifulSoup


@dataclass
class ParsedVariant:
    size: str = ""
    color: str = ""
    stock: int = 0
    price: Optional[float] = None
    source_id: str = ""


@dataclass
class ParsedProduct:
    source_url: str
    source_product_id: str
    title: str
    description: str = ""
    price: Optional[float] = None
    brand: str = ""
    image_urls: list = field(default_factory=list)
    variants: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)


class BaseParser:
    """Base class for all site parsers. Override parse_catalog and parse_product."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(
            headers=self.DEFAULT_HEADERS,
            timeout=30,
            follow_redirects=True,
        )

    def get(self, url: str) -> httpx.Response:
        response = self.client.get(url)
        response.raise_for_status()
        return response

    def soup(self, url: str) -> BeautifulSoup:
        response = self.get(url)
        return BeautifulSoup(response.text, "lxml")

    def parse_catalog(self, catalog_url: str) -> list[str]:
        """Return a list of product URLs found on a catalog/listing page."""
        raise NotImplementedError

    def parse_product(self, url: str) -> Optional[ParsedProduct]:
        """Parse a single product page into a ParsedProduct, or None on failure."""
        raise NotImplementedError

    def parse_product_for_sync(self, url: str) -> Optional[dict]:
        """
        Lightweight re-check for stock/price sync jobs — reuses parse_product
        but returns only the fields that matter for a periodic refresh, so
        callers don't have to re-parse the full product every time.
        """
        product = self.parse_product(url)
        if not product:
            return None
        return {
            "price": product.price,
            "variants": [
                {
                    "size": v.size,
                    "color": v.color,
                    "stock": v.stock,
                    "price": v.price,
                    "source_id": v.source_id,
                }
                for v in product.variants
            ],
        }

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
