# Web Scraper Demo

A small, self-contained example of the parser architecture I use for
catalog/product scraping projects (dropshipping supplier sync, price
monitoring, lead sourcing from public directories, etc.).

Runs against [books.toscrape.com](https://books.toscrape.com) — a public
sandbox site made specifically for scraping practice — so it's fully
reproducible without any credentials or private data.

## Design

- **`base.py`** — a `BaseParser` class + two dataclasses (`ParsedProduct`,
  `ParsedVariant`) that define a *source-agnostic* shape for scraped data.
  Every concrete parser translates one site's markup into this shape, so
  the rest of a pipeline (deduplication, database storage, periodic
  stock/price sync) never has to know which site a product came from.
- **`books_toscrape_parser.py`** — one concrete implementation: catalog
  page → list of product URLs, product page → `ParsedProduct`.
- **`run_demo.py`** — fetches a real category page, parses the first few
  products, and prints structured JSON.

In production use, this pattern lets me add a new source by writing one
new parser file (usually 60-150 lines) without touching anything else —
storage, sync jobs and deduplication logic stay the same.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py
```

## Stack

Python, httpx, BeautifulSoup4 + lxml.
