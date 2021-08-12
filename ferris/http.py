import aiohttp
import asyncio

from typing import Dict, Optional

from .types import DATA
from .utils import from_json
from . import __version__


class HTTPClient:
    MAX_TRIES = 3

    def __init__(self, token: str):
        self.__token: str = token
        user_agent: str = f"Ferrispy (https://github.com/Cryptex-github/ferrispy, {__version__})"
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(headers={"User-Agent": user_agent})

        self._buckets_lock: Dict[str, asyncio.Event] = {}
    
    async def request(self, url: str, method: str, **kwargs) -> Optional[Data]:
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
            async with self.__session.request(method, url, headers=headers, **kwargs) as response:
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
                    raise
                
                if response.status == 401:
                    raise

                if response.status == 403:
                    raise

                if 500 <= response.status < 600:
                    if tries == 1:
                        raise

                    continue
