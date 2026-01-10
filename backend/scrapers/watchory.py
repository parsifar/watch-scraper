import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class WatchoryHttpScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-CA,en;q=0.9",
        }

        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        product_cards = soup.select("li.product")

        for card in product_cards:
            card_text = card.get_text(" ", strip=True).lower()

            # -------------------------------------------------
            # Filter out refurbished products
            # -------------------------------------------------
            if "refurbished" in card_text:
                continue

            name_el = card.select_one("h3.card__heading a")
            if not name_el:
                continue

            name = name_el.get_text(strip=True)

            # -------------------------------------------------
            # Price extraction (lowest available price)
            # -------------------------------------------------
            price = None

            # Sale price (preferred)
            sale_price_el = card.select_one(
                ".price__sale .price-item--sale"
            )
            if sale_price_el:
                price = normalize_price(sale_price_el.get_text(strip=True))
            else:
                # Regular price fallback
                regular_price_el = card.select_one(
                    ".price__regular .price-item"
                )
                if regular_price_el:
                    price = normalize_price(
                        regular_price_el.get_text(strip=True)
                    )

            if price is None:
                continue

            products.append({
                "name": name,
                "price": price,
            })

        return products
