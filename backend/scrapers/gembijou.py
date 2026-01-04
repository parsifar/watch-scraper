import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class GemBijouHttpScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-CA,en;q=0.9",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.RequestException:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        products = []

        # Each product card
        product_cards = soup.select("#product-loop .product-index")

        for card in product_cards:
            # Product name
            name_el = card.select_one(".product-info h2")
            if not name_el:
                continue

            # ---- PRICE LOGIC ----
            # Prefer sale price if present, otherwise regular price
            price_el = (
                card.select_one(".price__sale .price-item--sale")
                or card.select_one(".price-item--regular")
            )

            if not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = normalize_price(price_el.get_text(strip=True))

            if price is not None:
                products.append({"name": name, "price": price})

        return products
