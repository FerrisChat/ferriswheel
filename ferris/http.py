from __future__ import annotations

import asyncio
from typing import Awaitable, Dict, Optional
from urllib.parse import quote

import aiohttp

from . import __version__
from .errors import FerrisUnavailable, Forbidden, NotFound, Unauthorized
from .types import Data, SupportsStr
from .utils import from_json

API_BASE_URL: str = 'https://api.ferris.chat/api/v0'


class APIRouter:
    def __init__(self, http: HTTPClient, route: str = '', /) -> None:
        self.__current_route: str = route
        self.__http_client: HTTPClient = http

    @property
    def url(self, /) -> str:
        return API_BASE_URL + self.__current_route

    def _make_new(self, route: str, /) -> APIRouter:
        return self.__class__(self.__http_client, route)

    def __getattr__(self, route: str, /) -> APIRouter:
        return self._make_new(f"{self.__current_route}/{route}")

    def __call__(self, route: SupportsStr, /) -> APIRouter:
        return self._make_new(f"{self.__current_route}/{quote(str(route))}")

    def request(self, method, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.__http_client.request(method, self.url, **kwargs)

    def get(self, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.request('GET', **kwargs)

    def post(self, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.request('POST', **kwargs)

    def put(self, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.request('PUT', **kwargs)

    def delete(self, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.request('DELETE', **kwargs)

    def patch(self, /, **kwargs) -> Awaitable[Optional[Data]]:
        return self.request('PATCH', **kwargs)


class HTTPClient:
    MAX_TRIES = 3

    def __init__(self, token: str, /):
        self.__token: str = token
        user_agent: str = (
            f"Ferrispy (https://github.com/Cryptex-github/ferrispy, {__version__})"
        )
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(
            headers={"User-Agent": user_agent}
        )

        self._buckets_lock: Dict[str, asyncio.Event] = {}

    async def request(self, url: str, method: str, /, **kwargs) -> Optional[Data]:
        bucket_key = f"{method} {url}"
        bucket = self._buckets_lock.get(bucket_key)
        if bucket is None:
            self._buckets_lock[bucket_key] = bucket = asyncio.Event()

        headers = {}

        if "data" in kwargs:
            headers["Content-Type"] = "application/json"

        if not bucket.is_set():
            await bucket.wait()

        for tries in range(self.MAX_TRIES):
            async with self.__session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                content = await response.text()

                if 400 > response.status >= 200:
                    return from_json(content)

                if response.status == 429:
                    data = from_json(content)
                    sleep = data.get("retry_after", 0)
                    bucket.clear()
                    await asyncio.sleep(sleep)
                    bucket.set()
                    continue

                if response.status == 404:
                    raise NotFound(response, content)

                if response.status == 401:
                    raise Unauthorized(response, content)

                if response.status == 403:
                    raise Forbidden(response, content)

                if 500 <= response.status < 600:
                    if tries == 1:
                        raise FerrisUnavailable(response, content)

                    continue
        return None
