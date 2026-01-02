from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class BijouxEcloreScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # for shopify sites (may not ever get to networkidle)
            await page.goto(url)

            # check if there's no results. If so return empty
            header = await page.query_selector("h1.page-header")
            if header:
                text = (await header.inner_text()).strip().lower()
                if text.startswith("0 results found"):
                    return []

            # we need to wait for the products to be loaded instead of networkidle
            await page.wait_for_selector("ul.productGrid>li.product")

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            # Example parsing logic: adapt selectors to actual site
            product_elements = soup.select(
                "ul.productGrid>li.product")  # adjust selector

            for el in product_elements:
                name_el = el.select_one(
                    ".card-information h3.card__heading a.card-title")
                price_el = el.select_one(
                    ".card-price .price__last .price-item")

                if name_el and price_el:
                    name = name_el.get_text(strip=True)
                    price = normalize_price(price_el.get_text(strip=True))
                    products.append({"name": name, "price": price})

            await browser.close()

        return products
