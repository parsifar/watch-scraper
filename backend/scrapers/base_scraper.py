from abc import ABC, abstractmethod


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str, term: str) -> list[dict]:
        """
        Scrapes the given URL and returns a list of products:
        [{"name": str, "price": float}, ...]
        """
        pass
