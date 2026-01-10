from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class CreationWatchesScraper(BaseScraper):
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
                ".product-list-item")  # adjust selector

            for el in product_elements:
                name_el = el.select_one(".txtSec>a p.product-name")

                # Price logic
                price_candidates = []

                # 1. Regular / discounted price (h3)
                h3 = el.select_one(".txtSec h3")

                if h3:
                    # Remove original price
                    del_tag = h3.find("del")
                    if del_tag:
                        del_tag.decompose()

                    price = normalize_price(h3.get_text(strip=True))
                    if price:
                        price_candidates.append(price)

                # 2. "With Code" price (h5)
                h5 = el.select_one(".txtSec h5")
                if h5:
                    price = normalize_price(h5.get_text(strip=True))
                    if price:
                        price_candidates.append(price)

                # 3. Choose lowest available price
                if name_el and price_candidates:
                    name = name_el.get_text(strip=True)
                    lowest_price = min(price_candidates)
                    products.append({
                        "name": name,
                        "price": lowest_price
                    })

            await browser.close()

        return products
