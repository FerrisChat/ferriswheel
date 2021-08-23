from __future__ import annotations

import aiohttp

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .http import HTTPClient
    from .types import Data


class Websocket:
    """The class that interfaces with FerrisChat's websockets."""

    def __init__(self, http: HTTPClient) -> None:
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


    async def connect(self) -> None:
        """Establishes a websocket connection with FerrisChat."""
        async for message in
