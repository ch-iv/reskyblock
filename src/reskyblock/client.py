import asyncio
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from functools import partial

from httpx import HTTPStatusError

from reskyblock.http import AbstractAsyncHTTPClient, HTTPXAsyncClient
from reskyblock.models import AllAuctions, Auctions, AuctionsEnded, Bazaar
from reskyblock.serialization import AbstractJSONDecoder, MSGSpecDecoder
from reskyblock.urls import _prepare_auctions_ended_url, _prepare_auctions_url, _prepare_bazaar_url

type APIEndpoint = Auctions | AuctionsEnded | Bazaar | AllAuctions
type APIEndpointGetter = Callable[[], Awaitable[APIEndpoint]]

__all__ = ("Client",)


class Client:
    def __init__(self) -> None:
        self._http_client: AbstractAsyncHTTPClient = HTTPXAsyncClient()
        self._json_decoder: AbstractJSONDecoder = MSGSpecDecoder()
        self._auctions_last_updated: int = 0
        self._auctions_ended_last_updated: int = 0
        self._bazaar_last_updated: int = 0

    async def get_auctions(self, page: int = 0) -> Auctions:
        """Get a single page of active auctions"""
        resp_bytes = await self._http_client.get(url=_prepare_auctions_url(page))
        auctions = self._json_decoder.serialize(resp_bytes, Auctions)
        self._auctions_last_updated = auctions.last_updated
        return auctions

    async def get_auctions_ended(self) -> AuctionsEnded:
        """Get ended auctions"""
        resp_bytes = await self._http_client.get(url=_prepare_auctions_ended_url())
        auctions_ended = self._json_decoder.serialize(resp_bytes, AuctionsEnded)
        self._auctions_ended_last_updated = auctions_ended.last_updated
        return auctions_ended

    async def get_bazaar(self) -> Bazaar:
        """Get bazaar endpoint"""
        resp_bytes = await self._http_client.get(url=_prepare_bazaar_url())
        bazaar = self._json_decoder.serialize(resp_bytes, Bazaar)
        self._bazaar_last_updated = bazaar.last_updated
        return bazaar

    async def get_all_auctions(self, max_pages: int = 100) -> AllAuctions:
        """Get auctions from all pages"""
        auctions = []
        page = 0
        last_updated = 0
        while page <= max_pages:
            try:
                auctions_page = await self.get_auctions(page)
                auctions.extend(auctions_page.auctions)
                last_updated = auctions_page.last_updated
                page += 1
            except HTTPStatusError:
                break
        return AllAuctions(last_updated, auctions)

    @staticmethod
    async def _get_continuous[T: APIEndpoint](
        getter: APIEndpointGetter, expected_update_interval: float, update_getter: APIEndpointGetter | None = None
    ) -> AsyncIterator[T]:
        use_update_getter_for_return = update_getter is None
        if update_getter is None:
            update_getter = getter

        last_updated = 0
        while 1:
            next_update = last_updated / 1000 + expected_update_interval
            if next_update > time.time():  # the next update is in the future
                sleep_for = next_update - time.time()
                await asyncio.sleep(max(sleep_for, 0.1))
            try:
                update_api_endpoint = await update_getter()
            except Exception as e:
                logging.exception(e)
                continue

            if update_api_endpoint.last_updated == last_updated:
                continue  # the API has not updated yet

            last_updated = update_api_endpoint.last_updated
            if use_update_getter_for_return:
                api_endpoint = update_api_endpoint
            else:
                try:
                    api_endpoint = await getter()
                except Exception as e:
                    logging.exception(e)
                    continue
            yield api_endpoint

    async def get_auctions_continuous(self) -> AsyncIterator[Auctions]:
        return self._get_continuous(self.get_auctions, 66.5)

    async def get_auctions_ended_continuous(self) -> AsyncIterator[AuctionsEnded]:
        return self._get_continuous(self.get_auctions_ended, 60)

    async def get_bazaar_continuous(self) -> AsyncIterator[Bazaar]:
        return self._get_continuous(self.get_bazaar, 20)

    async def get_all_auctions_continuous(self, max_pages: int = 100) -> AsyncIterator[list[Auctions]]:
        return self._get_continuous(partial(self.get_all_auctions, max_pages), 66.5, self.get_auctions)
