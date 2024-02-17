from reskyblock.http import AbstractHTTPClient, HTTPXClient
from reskyblock.models import Auctions, AuctionsEnded, Bazaar
from reskyblock.serialization import AbstractJSONDecoder, MSGSpecDecoder
from reskyblock.urls import _prepare_auctions_ended_url, _prepare_auctions_url, _prepare_bazaar_url

__all__ = ("Client",)


class Client:
    def __init__(self) -> None:
        self._http_client: AbstractHTTPClient = HTTPXClient()
        self._json_decoder: AbstractJSONDecoder = MSGSpecDecoder()

    def get_auctions(self, page: int = 0) -> Auctions:
        """Get a single page of active auctions"""
        resp_bytes = self._http_client.get(url=_prepare_auctions_url(page))
        return self._json_decoder.serialize(resp_bytes, Auctions)

    def get_auctions_ended(self) -> AuctionsEnded:
        """Get ended auctions"""
        resp_bytes = self._http_client.get(url=_prepare_auctions_ended_url())
        return self._json_decoder.serialize(resp_bytes, AuctionsEnded)

    def get_bazaar(self) -> Bazaar:
        """Get bazaar endpoint"""
        resp_bytes = self._http_client.get(url=_prepare_bazaar_url())
        return self._json_decoder.serialize(resp_bytes, Bazaar)
