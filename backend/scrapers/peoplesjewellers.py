from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class PeoplesJewellersScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to the URL
            await page.goto(url, timeout=30000)

            # Wait for either search grid or no-results / single product
            try:
                await page.wait_for_selector(
                    ".product-grid, div.no-result-title, .product-detail__summary--name",
                    timeout=5000
                )
            except:
                # If nothing loads, return empty
                await browser.close()
                return []

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # --- Case 1: Multiple products ---
            product_elements = soup.select(".product-grid .prod-row-item")
            for el in product_elements:
                name_el = el.select_one(
                    ".product-grid_tile_details .product-tile-description a")
                price_el = el.select_one(".product-prices .price .plp-align")

                # Remove discount badge if present
                if price_el:
                    discount = price_el.select_one("app-amor-tags")
                    if discount:
                        discount.decompose()

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            # --- Case 2: Single product page --- (the site auto redirects)
            if not products:
                name_el = soup.select_one(".product-detail__summary--name h1")
                price_el = soup.select_one(
                    ".product-detail__summary--price .product-price__price")

                if price_el:
                    discount = price_el.select_one("app-amor-tags")
                    if discount:
                        discount.decompose()

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
