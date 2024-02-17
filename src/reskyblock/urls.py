"""URLs for the SkyBlock API"""
import random

_AUCTIONS_URL = "https://api.hypixel.net/v2/skyblock/auctions"
_AUCTIONS_ENDED_URL = "https://api.hypixel.net/v2/skyblock/auctions_ended"
_BAZAAR_URL = "https://api.hypixel.net/v2/skyblock/bazaar"


def _prepare_auctions_url(page: int | None = None) -> str:
    if page is None:
        page = 0
    return f"{_AUCTIONS_URL}?page={page}&page={random.randint(10000, 2147483646)}"  # noqa: S311


def _prepare_auctions_ended_url() -> str:
    return _AUCTIONS_ENDED_URL


def _prepare_bazaar_url() -> str:
    return _BAZAAR_URL
