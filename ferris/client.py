import asyncio

from .http import APIRouter, HTTPClient

__all__ = ('Client',)


class Client:
    """Represents a client connection to FerrisChat.

    Parameters
    ----------
    ...
    """

    __slots__ = ('loop', 'api')

    def __init__(self, /) -> None:
        self.loop = asyncio.get_event_loop()

    async def start(self, token: str, /) -> None:
        http = HTTPClient(token)
        self.api = APIRouter(http)

    def run(self, *args, **kwargs):
        asyncio.run(self.start(), *args, **kwargs)
