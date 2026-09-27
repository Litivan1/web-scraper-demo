"""
Runs the parser end-to-end against a real public page and prints the
structured result, so you can verify the whole pipeline works without
needing a database or any other project scaffolding.

    python run_demo.py
"""
import json
from dataclasses import asdict

from books_toscrape_parser import BooksToScrapeParser

CATALOG_URL = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"


def main():
    with BooksToScrapeParser(base_url="https://books.toscrape.com") as parser:
        product_urls = parser.parse_catalog(CATALOG_URL)
        print(f"Found {len(product_urls)} products in catalog\n")

        results = []
        for url in product_urls[:5]:
            product = parser.parse_product(url)
            if product:
                results.append(asdict(product))

        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
