from __future__ import annotations

import asyncio
import concurrent
import logging
import sys
import threading
import time
import traceback
from types import coroutine
from typing import TYPE_CHECKING, Coroutine, Dict, Union, Any

import aiohttp

from .errors import Reconnect, WebsocketException
from .handler import EventHandler
from .utils import from_json, to_json

if TYPE_CHECKING:
    from .client import Client
    from .http import HTTPClient
    from .types import Data
    from .types.ws import WsConnectionInfo


log = logging.getLogger(__name__)


class KeepAliveManager(threading.Thread):
    def __init__(self, ws: Websocket, /) -> None:
        self._ws = ws

        self._interval: int = 45
        self._stop_event: threading.Event = threading.Event()

        self._max_heartbeat_timeout: int = ws._max_heartbeat_timeout

        self._last_ack: float = time.perf_counter()
        self._last_send: float = time.perf_counter()
        self._last_recv: float = time.perf_counter()
        self._latency: float = float('inf')

        super().__init__(name="FerrisWheel-KeepAliveManager", daemon=True)

    def run(self) -> None:
        while not self._stop_event.wait(self._interval):
            if self._last_recv + self._max_heartbeat_timeout < time.perf_counter():
                log.warning('Websocket stopped responding to gateway. Reconnecting.')
                coro = self._ws.close(4000)
                f = asyncio.run_coroutine_threadsafe(coro, self._ws._loop)

                try:
                    f.result()
                except Exception as e:
                    log.exception(f'Exception {e} raised while reconnecting websocket.')
                finally:
                    self.stop()
                    return

            f = self.ping()

            try:
                blocked_for: int = 0

                while True:
                    try:
                        f.result(10)
                        break
                    except concurrent.futures.TimeoutError:
                        blocked_for += 10
                        try:
                            frame = sys._current_frames()[self._ws._main_thread_id]
                        except KeyError:
                            m = self.block_message
                        else:
                            stack: str = ''.join(traceback.format_stack(frame))
                            m: str = f'{self.block_message}\nLoop Threadtraceback: (most recent call last):\n{stack}'

                        log.warning(m, blocked_for)
            except Exception as e:
                log.exception(f'Exception {e} raised while sending ping.')
                self.stop()
                return
            else:
                self._last_send = time.perf_counter()

    def ping(self) -> asyncio.Future:
        coro = self._ws.send(self.ping_payload)
        return asyncio.run_coroutine_threadsafe(coro, self._ws._loop)

    def pong(self) -> asyncio.Future:
        coro = self._ws.send(self.pong_payload)
        return asyncio.run_coroutine_threadsafe(coro, self._ws._loop)

    def stop(self) -> None:
        self._stop_event.set()

    def tick(self) -> None:
        self._last_recv = time.perf_counter()

    def ack(self) -> None:
        self._last_ack = time.perf_counter()
        self._latency = self._last_ack - self._last_send

        if self._latency > 10:
            log.warning(f'Websocket is {self._latency:.1f} seconds behind.')

    @property
    def latency(self) -> float:
        """
        The latency of the websocket.
        """
        return self._latency

    @property
    def block_message(self) -> str:
        """Returns the message to be logged when heartbeat is blocked."""
        return 'Websocket heartbeat blocked for more than %s seconds'

    @property
    def ping_payload(self) -> Dict[str, str]:
        """Returns the ping payload to be sent to the websocket."""
        return {'c': 'Ping'}

    @property
    def pong_payload(self) -> Dict[str, str]:
        """Returns the pong payload to be sent to the websocket."""
        return {'c': 'Pong'}


class Websocket:
    """The class that interfaces with FerrisChat's websockets."""

    def __init__(self, client: Client) -> None:
        self.ws: aiohttp.ClientWebSocketResponse
        self._http: HTTPClient = client._connection._http
        self._loop: asyncio.AbstractEventLoop = client._connection.loop

        self._max_heartbeat_timeout: int = client._connection._max_heartbeat_timeout
        self._main_thread_id: int = threading.get_ident()
        self._heartbeat_manager: KeepAliveManager = KeepAliveManager(self)
        self._handler: EventHandler = EventHandler(
            client._connection, self._heartbeat_manager
        )

        self.dispatch: Coroutine = client.dispatch
        self._ws_url: str = ''

    async def prepare(self) -> None:
        """Retrieves the URL needed for websocket connection."""
        response: WsConnectionInfo = await self._http.api.ws.info.get()  # type: ignore
        self._ws_url = response['url']

    def handle(self, data: Dict[Any, Any], /) -> None:
        """Handles a message received from the websocket."""
        log.debug(f'Received: {data}')
        self._handler.handle(data)

    def _parse_and_handle(self, data: Union[str, bytes], /) -> None:
        self._heartbeat_manager.tick()

        if isinstance(data, (str, bytes)):
            _data: dict = from_json(data)
            self.handle(_data)

    async def send(self, data: Dict[Any, Any], /) -> None:
        _data = to_json(data)
        await self.ws.send_str(_data)

    async def connect(self) -> None:
        """Establishes a websocket connection with FerrisChat."""
        if not self._ws_url:
            await self.prepare()

        self.ws = await self._http.session.ws_connect(self._ws_url)

        await self.send(
            {'c': 'Identify', 'd': {'token': self._http.token, 'intents': 0}}
        )

        if not self._heartbeat_manager.is_alive():
            self._heartbeat_manager.start()

        self.dispatch('connect')
        async for message in self.ws:
            if message.type in {aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY}:
                self._parse_and_handle(message.data)
            elif message.type is aiohttp.WSMsgType.ERROR:
                log.error(f'Websocket error: {message.data}')
                raise WebsocketException(message.data)
            elif message.type in (
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
                aiohttp.WSMsgType.CLOSE,
            ):
                log.info('Websocket closed, attempting to reconnect.')
                self._heartbeat_manager.stop()
                raise Reconnect

    async def close(self, code: int) -> None:
        """Closes the current websocket connection."""
        if ws := getattr(self, 'ws', None):
            if self._heartbeat_manager.is_alive():
                self._heartbeat_manager.stop()

            if not ws.closed:
                await self.ws.close(code=code)
