from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price

# Shopify site scraper


class BigTimeScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # for shopify sites (may not ever get to networkidle)
            await page.goto(url)

            # if there's no results, return empty
            if await page.locator("div.no-results").count() > 0:
                return []

            # we need to wait for the products to be loaded instead of networkidle
            await page.wait_for_selector("#SearchLoop .product-item")

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Example parsing logic: adapt selectors to actual site
            product_elements = soup.select(
                "#SearchLoop .product-item .product-information")  # adjust selector

            for el in product_elements:
                name_el = el.select_one(".product-item__title")
                price_el = el.select_one(
                    ".product-item__price span.new-price .money")

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
