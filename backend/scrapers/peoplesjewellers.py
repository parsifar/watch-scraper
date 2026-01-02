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

            await page.goto(url)

            # we need to wait for the products to be loaded instead of networkidle
            await page.wait_for_selector(".product-grid , div.no-result-title")

            # if there's no results, return empty
            if await page.locator("div.no-result-title").count() > 0:
                return []

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Example parsing logic: adapt selectors to actual site
            product_elements = soup.select(
                ".product-grid .prod-row-item")  # adjust selector

            for el in product_elements:
                name_el = el.select_one(
                    ".product-grid_tile_details .product-tile-description a")
                price_el = el.select_one(".product-prices .price .plp-align")

                # remove discount badge
                discount = price_el.select_one("app-amor-tags")
                if discount:
                    discount.decompose()

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
