from .watchit import WatchItScraper
from .watchory import WatchoryScraper
from .bigtimewatches import BigTimeScraper
from .citywatches import CityWatchesScraper
from .ebay import EbayScraper
from .bijouxeclore import BijouxEcloreScraper
from .kavarjewellers import KavarJewellersScraper
from .peoplesjewellers import PeoplesJewellersScraper
from .creationwatches import CreationWatchesScraper
from .canadawatchhouse import CanadaWatchHouseScraper
from .assaleh import AssalehScraper

DOMAIN_SCRAPER = {
    "watchit.ca": WatchItScraper,
    "watchory.ca": WatchoryScraper,
    "bigtimewatches.com": BigTimeScraper,
    "citywatches.ca": CityWatchesScraper,
    "ebay.ca": EbayScraper,
    "bijouxeclore.com": BijouxEcloreScraper,
    "kavarjewellers.ca": KavarJewellersScraper,
    "peoplesjewellers.com": PeoplesJewellersScraper,
    "creationwatches.com": CreationWatchesScraper,
    "canadawatchhouse.ca": CanadaWatchHouseScraper,
    "assaleh.ca": AssalehScraper,
}
