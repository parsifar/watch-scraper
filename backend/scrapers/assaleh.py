from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class AssalehScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Example parsing logic: adapt selectors to actual site
            product_elements = soup.select(
                "ul.list-view-items li.list-view-item")  # adjust selector

            for el in product_elements:
                name_el = el.select_one(
                    ".list-view-item__link .list-view-item__title-column .product-card__title")
                price_el = el.select_one(
                    ".list-view-item__link .list-view-item__price-column .price-item--sale")

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
