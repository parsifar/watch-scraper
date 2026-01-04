from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class WatchItScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Go to the search URL
            await page.goto(url, timeout=30000)

            # Wait for either products or "no results" message
            try:
                await page.wait_for_selector(
                    "li.snize-product-in-stock, div.search-no-results",
                    timeout=5000
                )
            except:
                # Nothing loaded, return empty
                await browser.close()
                return []

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # --- Case 1: Products found ---
            product_elements = soup.select("li.snize-product-in-stock")
            for el in product_elements:
                name_el = el.select_one("span.snize-title")
                price_el = el.select_one("span.snize-price")

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            # --- Case 2: No products ---
            if not products:
                no_results = soup.select_one("div.search-no-results")
                if no_results:
                    # Explicitly return empty
                    products = []

            await browser.close()

        return products
