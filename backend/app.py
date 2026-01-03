from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, HttpUrl, constr
from urllib.parse import urlparse
from backend.scrapers import DOMAIN_SCRAPER
from backend.relevance import filter_results
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# read the env variables from the .env file and add them to the current OS environment variables to be read by os.getenv
load_dotenv()

ENV = os.getenv(key="ENV", default="development")
RATE_LIMIT_PER_MINUTE = os.getenv(key="RATE_LIMIT_PER_MINUTE", default=11)


ALLOWED_DOMAINS = set(DOMAIN_SCRAPER.keys())

# rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Retailer Price Scraper")
app.state.limiter = limiter


class SearchRequest(BaseModel):
    """Define request model with Pydantic"""
    url: HttpUrl
    term: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=100
    )  # type: ignore


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests"}
    )


@app.post("/extract-price")
# 3 searches * 11 retailers per minute
@limiter.limit(RATE_LIMIT_PER_MINUTE+"/minute")
async def search_products(request: Request):
    body = await request.json()
    search_req = SearchRequest(**body)

    # parse the URL and check that it's not file://, ftp://, etc.
    parsed_url = urlparse(str(search_req.url))

    if parsed_url.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid URL scheme")

    # Extract domain from the URL
    domain = parsed_url.netloc.replace("www.", "")

    # check that the requested domain is in allowed retailer domains (to prevent SSRF)
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail="Domain not allowed"
        )

    # Lookup scraper class for this domain
    scraper_class = DOMAIN_SCRAPER.get(domain)
    if not scraper_class:
        # If no scraper exists for this domain, return 400 error
        raise HTTPException(
            status_code=400, detail=f"No scraper available for domain '{domain}'")

    # Instantiate scraper
    scraper = scraper_class()

    try:
        # Call the scraper to get products
        # Convert request.url to string before passing, because scrapers usually expect strings
        products = await scraper.scrape(str(search_req.url), search_req.term)
    except Exception as e:
        # Catch any scraping errors and return 500
        raise HTTPException(
            status_code=500, detail=f"Scraping failed: {str(e)}")

    if not products:
        # If scraper returns empty list, return 404
        raise HTTPException(status_code=404, detail="No products found")

    # filter results and remove the unrelated ones
    filtered_products = filter_results(search_req.term, products)

    if filtered_products:
        # Find the product with the minimum price
        min_product = min(filtered_products, key=lambda x: x["price"])
        # Return the scraped products as JSON
        return {"filtered_products":  filtered_products, "starting_from": min_product["price"]}
    else:
        # If filtered products is empty, return all products
        min_product = min(products, key=lambda x: x["price"])
        return {"all_products":  products, "starting_from": min_product["price"]}

# Serve frontend last
app.mount("/", StaticFiles(directory=BASE_DIR /
          "static", html=True), name="static")
