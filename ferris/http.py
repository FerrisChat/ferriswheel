import asyncio
from typing import Dict

import aiohttp

from . import __version__


class HTTPClient:
    def __init__(self, token: str):
        self.__token: str = token
        user_agent: str = f"Ferrispy (https://github.com/Cryptex-github/ferrispy, {__version__})"
        self.__session: aiohttp.ClientSession = aiohttp.ClientSession(headers={"User-Agent": user_agent})

        self._global_ratelimited: asyncio.Event = asyncio.Event()
        self._buckets_lock: Dict[str, asyncio.Lock] = {}
    
    
    
