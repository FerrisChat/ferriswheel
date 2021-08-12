import asyncio
from typing import Dict, Optinal

import aiohttp

from .types import DATA
from . import __version__


class HTTPClient:
    MAX_TRIES = 3

    def __init__(self, token: str):
        self.__token: str = token
        user_agent: str = f"Ferrispy (https://github.com/Cryptex-github/ferrispy, {__version__})"
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(headers={"User-Agent": user_agent})

        self._global_ratelimited: asyncio.Event = asyncio.Event()
        self._buckets_lock: Dict[str, asyncio.Event] = {}
    
    async def request(self, url: str, method: str, **kwargs) -> Optinal[DATA]:
        bucket_key = f"{method} {url}"
        bucket = self._buckets_lock.get(bucket_key)
        if bucket is None:
            self._buckets_lock[bucket_key] = bucket = asyncio.Event()
        
        headers = {}
        
        if "data" in kwargs:
            headers["Content-Type"] = "application/json"
        
        if not self._global_ratelimited.is_set():
            await self._global_ratelimited.wait()
        
        if not bucket.is_set():
            await bucket.wait()
        
        for tries in range(self.MAX_TRIES):
            async with self.__session.request(method, url, headers=headers, **kwargs) as response:
                content = await response.text()

                try:
                    

