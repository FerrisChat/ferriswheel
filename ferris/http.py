from __future__ import annotations

import asyncio
from typing import Awaitable, ClassVar, Dict, Optional
from urllib.parse import quote

import aiohttp

from . import __version__
from .errors import (
    BadRequest,
    FerrisUnavailable,
    Forbidden,
    HTTPException,
    NotFound,
    Unauthorized,
)
from .types import Data, SupportsStr
from .utils import from_json


__all__ = (
    'APIRouter',
    'HTTPClient',
)


class APIRouter:
    __slots__ = ('__current_route', '__http_client')

    def __init__(self, http: HTTPClient, route: str = '', /) -> None:
        self.__current_route: str = route
        self.__http_client: HTTPClient = http

    @property
    def url(self, /) -> str:
        return HTTPClient.API_BASE_URL + self.__current_route

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
    API_BASE_URL: ClassVar[str] = 'https://api.ferris.chat/v0'

    MAX_TRIES: ClassVar[int] = 3
    USER_AGENT: ClassVar[str] = (
        f"FerrisWheel (https://github.com/Cryptex-github/ferriswheel v{__version__})"
    )

    __slots__ = ('__token', '__session', '_buckets_lock', '_api_router')

    def __init__(self, token: str, /) -> None:
        self.__token: str = token
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(
            headers={"User-Agent": self.USER_AGENT, "Authorization": self.__token}
        )

        self._buckets_lock: Dict[str, asyncio.Event] = {}
        self._api_router: APIRouter = APIRouter(self)

    @property
    def api(self) -> APIRouter:
        return self._api_router

    @classmethod
    async def from_email_and_password(
        cls,
        email: str,
        password: str,
        id: int
    ) -> HTTPClient:
        for tries in range(cls.MAX_TRIES):
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.API_BASE_URL}/auth/{id}",
                    headers={"Email": email, "Password": password},
                ) as response:
                    content = await response.text()

                    if 400 > response.status >= 200:
                        token = from_json(content)['token']
                        return cls(token)

                    if response.status == 400:
                        data = from_json(content)
                        reason = data.get('reason')
                        location = data.get('location', {})
                        line = location.get('line')
                        character = location.get('character')

                        raise BadRequest(
                            response, f"{reason}\nLine: {line} Character: {character}"
                        )

                    if response.status == 404:
                        raise NotFound(response, content)

                    if response.status == 401:
                        raise Unauthorized(response, content)

                    if response.status == 403:
                        raise Forbidden(response, content)

                    if 500 <= response.status < 600:
                        if tries == 1:
                            try:
                                data = from_json(content)
                                reason = data.get('reason')
                            except:  # TODO: Fix broad except
                                reason = content

                            raise FerrisUnavailable(response, reason)

                        continue

                    raise HTTPException(response, content)

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

                if response.status == 400:
                    data = from_json(content)
                    reason = data.get('reason')
                    location = data.get('location', {})
                    line = location.get('line')
                    character = location.get('character')
                    raise BadRequest(
                        response, f"{reason}\nLine: {line} Character: {character}"
                    )

                if response.status == 404:
                    raise NotFound(response, content)

                if response.status == 401:
                    raise Unauthorized(response, content)

                if response.status == 403:
                    raise Forbidden(response, content)

                if 500 <= response.status < 600:
                    if tries == 1:
                        try:
                            data = from_json(content)
                            reason = data.get('reason')
                        except:  # TODO: Fix broad except
                            reason = content

                        raise FerrisUnavailable(response, reason)
                    continue

                raise HTTPException(response, content)
