from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from .utils import normalize_price


class KavarJewellersScraper(BaseScraper):
    async def scrape(self, url: str, term: str) -> list[dict]:
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # for this Wix sites that loads the product grid in an iframe
            await page.goto(url)
            # we need to wait for the iframe if the products grid to load
            await page.wait_for_selector('iframe[title="Online Store"]')
            # get all iframes
            iframes = await page.query_selector_all('iframe[title="Online Store"]')
            # we need the third one
            iframe_element = iframes[2]
            # Get the iframe’s Frame object
            frame = await iframe_element.content_frame()

            # Wait for products inside the iframe (or the not-result div)
            await frame.wait_for_selector(".grid-product,div.ec-search--no-products", timeout=10000)

            # if there's no results, return empty
            if await frame.locator("div.ec-search--no-products").count() > 0:
                return []

            # get in-stock items
            items = frame.locator(
                ".grid-product:not(.ec-store-productsGrid-cell-outOfStock)")
            count = await items.count()

            for i in range(count):
                item = items.nth(i)

                name = await item.locator(
                    "a.grid-product__title .grid-product__title-inner"
                ).inner_text()

                price = await item.locator(
                    ".grid-product__price .grid-product__price-value"
                ).inner_text()

                if name and price:
                    products.append({
                        "name": name.strip(),
                        "price": normalize_price(price)
                    })

            await browser.close()

        return products
