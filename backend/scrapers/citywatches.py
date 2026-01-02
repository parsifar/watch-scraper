from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class CityWatchesScraper(BaseScraper):
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
                "ul#collection>li:not(.unavailable)")  # adjust selector

            for el in product_elements:
                name_el = el.select_one("h3>a")
                price_el = el.select_one("p.price")
                # Remove the old price span (Specific for City Watches site)
                if price_el.span:
                    price_el.span.extract()

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
