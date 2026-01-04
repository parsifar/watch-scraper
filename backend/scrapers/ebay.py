import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class EbayHttpScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        """
        Scrape eBay search results via direct HTTP requests (no browser).

        Returns a list of dicts: [{"name": str, "price": float}]
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-CA,en;q=0.9",
        }

        # Make HTTP GET request
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()  # raise error if non-200

        soup = BeautifulSoup(resp.text, "html.parser")

        products = []

        # Each search item
        for el in soup.select("ul.srp-results>li"):
            name_el = el.select_one(
                ".su-card-container__header .s-card__link .s-card__title span.primary")
            price_el = el.select_one(
                ".su-card-container__attributes span.s-card__price")

            if name_el and price_el:
                name_text = name_el.get_text(strip=True)

                # eBay sometimes includes "New Listing" as text
                if name_text.lower() == "new listing":
                    # skip this element
                    continue

                price_text = price_el.get_text(strip=True)
                price = normalize_price(price_text)

                if price is not None:
                    products.append({"name": name_text, "price": price})

        return products
