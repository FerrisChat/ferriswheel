import asyncio

from .connection import Connection


__all__ = ('Client',)


class Client:
    """Represents a client connection to FerrisChat.

    Parameters
    ----------
    ...
    """

    __slots__ = ('loop', 'api', '_connection')

    def __init__(self, /, loop: asyncio.AbstractEventLoop = None, **options) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self._connection: Connection = Connection(self.loop, **options)

    def _initialize_connection(self, token: str, /) -> None:
        self._connection._initialize_http(token)

    async def start(self, token: str, /) -> None:
        self._initialize_connection(token)

    def run(self, *args, **kwargs):
        asyncio.run(self.start(), *args, **kwargs)
