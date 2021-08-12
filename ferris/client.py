import asyncio

from .http import APIRouter, HTTPClient


class Client:
    """Represents a client connection to FerrisChat.
    
    Parameters
    ----------
    ...
    """
    
    def __init__(self, /) -> None:
        self.loop = asyncio.get_event_loop()

    async def start(self, token: str, /) -> None:
        ...
    
    def run(self, *args, **kwargs):
        asyncio.run(self.start(), *args, **kwargs)
