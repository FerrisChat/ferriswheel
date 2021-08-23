from __future__ import annotations

import aiohttp
from typing import TYPE_CHECKING, Union

from .utils import to_json

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types import Data


class Websocket:
    """The class that interfaces with FerrisChat's websockets."""

    def __init__(self, http: HTTPClient) -> None:
        self.ws: aiohttp.ClientWebSocketResponse = None

        self._http: HTTPClient = http
        self._ws_url: str = None

    async def prepare(self) -> None:
        """Retrieves the URL needed for websocket connection."""
        response = await self._http.api.ws.info.get()
        self._ws_url = response['url']

    async def handle(self, data: Data) -> None:
        """Handles a message received from the websocket."""
        ...  # not implemented

    async def _parse_and_handle(self, data: Union[str, bytes]) -> None:
        if isinstance(data, (str, bytes)):
            data = to_json(data)
            await self.handle(data)

    async def connect(self) -> None:
        """Establishes a websocket connection with FerrisChat."""
        if not self._ws_url:
            await self.prepare()

        self.ws = await self._http.session.ws_connect(self._ws_url)

        async for message in self.ws:
            if message.type in {aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY}:
                await self._parse_and_handle(message.data)
            elif message.type is aiohttp.WSMsgType.ERROR:
                raise  # TODO: Make error for this
            elif message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSE):
                raise  # TODO: Reconnect here

    async def close(self) -> None:
        """Closes the current websocket connection."""
        await self.ws.close()
