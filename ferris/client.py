from __future__ import annotations

import asyncio
import logging
import signal
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    overload,
)

from ferris.types import message

from .channel import Channel
from .connection import Connection
from .errors import Reconnect, WebsocketException
from .guild import Guild
from .invite import Invite
from .message import Message
from .user import ClientUser, User
from .utils import sanitize_id
from .websocket import Websocket

if TYPE_CHECKING:
    from .types import Id

log = logging.getLogger(__name__)

__all__ = ('Dispatcher', 'Client')

# https://github.com/Rapptz/discord.py/blob/main/discord/client.py#L81
# https://github.com/python/cpython/blob/main/Lib/asyncio/runners.py


def _cancel_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    log.info(f'Cancelling {len(tasks)} tasks.')

    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    log.info('Cancelled all tasks.')

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    'message': 'Unhandled exception during Client.run shutdown.',
                    'exception': task.exception(),
                    'task': task,
                }
            )


def _cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        log.info('Closing the event loop.')
        loop.close()


class Dispatcher:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop: asyncio.AbstractEventLoop = loop
        self.event_handlers: defaultdict[
            str, List[Callable[..., Awaitable]]
        ] = defaultdict(list)

    async def wrap_event(
        self, coro: Callable[..., Awaitable]
    ) -> Callable[..., Awaitable]:
        try:
            await coro
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            self.dispatch('error', exc)

    def dispatch(self, event: str, *args, **kwargs) -> asyncio.Future:
        coros = []

        if callback := getattr(self, f'on_{event}', False):
            coros.append(callback(*args, **kwargs))

        if callbacks := self.event_handlers.get(event):
            coros += [self.wrap_event(cb(*args, **kwargs)) for cb in callbacks]

        return asyncio.ensure_future(asyncio.gather(*coros))

    def add_listener(self, event: str, callback: Callable[..., Awaitable]) -> None:
        if event.startswith('on_'):
            event = event[3:]

        self.event_handlers[event].append(callback)

    def remove_listener(self, event: str, callback: Callable[..., Awaitable]) -> None:
        if event.startswith('on_'):
            event = event[3:]

        self.event_handlers[event].remove(callback)

    def clear_listeners(self) -> None:
        self.event_handlers.clear()

    def stop_listening_to(self, event: str, /) -> None:
        if event.startswith('on_'):
            event = event[3:]

        self.event_handlers[event].clear()
        del self.event_handlers[event]

    def listen(self, event: Optional[str] = None):
        def decorator(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
            store = event

            if store is None:
                store = func.__name__

            if store.startswith('on_'):
                store = store[3:]

            self.add_listener(store, func)
            return func

        return decorator

    def event(self, func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        event = func.__name__

        if not event.startswith('on_'):
            event = 'on_' + event

        setattr(self, event, func)

        return func


class EventTemplateMixin:
    async def on_login(self) -> None:
        """|coro|

        Called when the client has logged in.
        """
        pass

    async def on_close(self) -> None:
        """|coro|

        Called when the client is closing.
        This could be used for clean-up/memory freeing.
        """
        pass

    async def on_connect(self) -> None:
        """|coro|
        Called when the client has connected to FerrisChat ws.
        """
        pass

    async def on_error(self, error: Exception) -> None:
        """|coro|

        Called when an exception is raised in an event handler.
        """
        pass


class Client(Dispatcher, EventTemplateMixin):
    """Represents a client connection to FerrisChat.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The event loop to use for the client. If not passed, then the default event loop is used.
    max_messages_count: Optional[int]
        The maximum number of messages to store in the internal message buffer.
        Defaults to ``1000``.

    max_heartbeat_timeout: Optional[int]
        The maximum timeout in seconds between sending a heartbeat to the server.
        If heartbeat took longer than this timeout, the client will attempt to reconnect.
    """

    def __init__(
        self, /, loop: Optional[asyncio.AbstractEventLoop] = None, **options
    ) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self._is_closed: bool = False
        self._connection: Connection = Connection(self.loop, self.dispatch, **options)
        self._is_ready = self._connection._is_ready
        super().__init__(self.loop)

    @property
    def user(self) -> Optional[ClientUser]:
        """Returns the connected :class:`~ClientUser`"""
        return self._connection.user

    @property
    def latency(self) -> float:
        """Returns the websocket latency between the client and the server."""
        if ws := getattr(self, 'ws', None):
            return self.ws._heartbeat_manager.latency
        return float('inf')

    @property
    def is_ready(self) -> bool:
        """Returns whether the client is ready to use."""
        return self._is_ready.done()

    @property
    def is_closed(self) -> bool:
        """Returns whether the client is closed."""
        return self._is_closed

    async def wait_until_ready(self) -> None:
        """|coro|

        Waits until the client is ready to use.
        """
        return await self._is_ready

    @property
    def guilds(self) -> List[Guild]:
        """Returns a list of the client's guilds."""
        return list(self._connection._guilds.values())

    async def join_guild(self, code: str) -> None:
        """|coro|

        Joins a guild with an invite code.

        Parameters
        ----------
        code: str
            The invite code to use.
        """
        await self._connection.api.invites(code).post()

    async def create_bot(self, name: str) -> User:
        """|coro|

        Creates a bot account.

        Parameters
        ----------
        name: str
            The name of the bot.

        Returns
        -------
        :class:`User`
        """
        u = await self._connection.api.users(self.user.id).bots.post({'username': name})
        return User(u, self._connection)

    async def fetch_invite(self, code: str) -> None:
        """|coro|

        Fetches an invite by code.

        Parameters
        ----------
        code: str
            The invite code to fetch.
        """
        i = await self._connection.api.invites(code).get()
        return Invite(self._connection, i)

    async def create_guild(self, name: str) -> Guild:
        """|coro|

        Creates a new guild.

        Parameters
        ----------
        name: str
            The name of the guild.

        Returns
        -------
        :class:`Guild`
            The guild created.
        """
        g = await self._connection.api.guilds.post(json={'name': name})
        return Guild(self._connection, g)

    async def fetch_self(self, cache: bool = True) -> ClientUser:
        """|coro|

        Fetches the client's user.

        Parameters
        ----------
        cache: bool
            Whether to cache the user. Defaults to ``True``.

        Returns
        -------
        :class:`ClientUser`
            The client's user.
        """
        u = await self._connection.api.users.me.get()

        if cache:
            u = self._connection.user
            u._process_data(u)
        else:
            u = ClientUser(self._connection, u)

        return u

    def get_message(self, id: Id) -> Optional[Message]:
        """
        Gets a message from the internal message buffer.

        Parameters
        ----------
        id: int
            The ID of the message to get.

        Returns
        -------
        Optional[:class:`Message`]
            The message with the given ID, or ``None`` if it does not exist.
        """
        id = sanitize_id(id)
        return self._connection.get_message(id)

    def get_channel(self, id: Id) -> Optional[Channel]:
        """
        Gets a channel from the internal channel buffer.

        Parameters
        ----------
        id: int
            The ID of the channel to get.

        Returns
        -------
        Optional[:class:`Channel`]
            The channel with the given ID, or ``None`` if it does not exist.
        """
        id = sanitize_id(id)
        return self._connection.get_channel(id)

    def get_user(self, id: Id) -> Optional[User]:
        """
        Gets a user from the internal user buffer.

        Parameters
        ----------
        id: int
            The ID of the user to get.

        Returns
        -------
        Optional[:class:`User`]
            The user with the given ID, or ``None`` if it does not exist.
        """
        id = sanitize_id(id)
        return self._connection.get_user(id)

    async def fetch_message(self, id: Id, *, cache: bool = False) -> Message:
        """|coro|

        Fetches a message from the internal message buffer.

        Parameters
        ----------
        id: int
            The ID of the message to fetch.

        cache: Optional[bool]
            Whether to cache the message in the internal message cache.
            Defaults to ``False``.

        Returns
        -------
        :class:`Message`
            The message with the given ID.
        """
        id = sanitize_id(id)
        m = await self._connection.api.messages(id).get()

        m = Message(self._connection, m)

        if cache:
            self._connection.store_message(m)

        return m

    async def ping(self) -> None:
        """|coro|

        Pings the server. This will ping the REST API not ws.
        If you want ws latency, use :attr:`latency` instead.
        """
        await self._connection.api.ping.get()

    async def fetch_channel(self, id: Id, *, cache: bool = False) -> Channel:
        """|coro|

        Fetches a channel by ID.

        Parameters
        ----------
        id: int
            The ID of the channel to fetch.

        cache: Optional[bool]
            Whether to cache the channel in the internal channel cache.

        Returns
        -------
        :class:`Channel`
            The channel with the given ID.
        """
        id = sanitize_id(id)
        c = await self._connection.api.channels(id).get()

        c = Channel(self._connection, c)

        if cache:
            self._connection.store_channel(c)

        return c

    async def fetch_user(self, id: Id, *, cache: bool = False) -> User:
        """|coro|

        Fetches a user by ID.

        Parameters
        ----------
        id: int
            The ID of the user to fetch.

        cache: Optional[bool]
            Whether to cache the user in the internal user cache.

        Returns
        -------
        :class:`User`
            The user with the given ID.
        """
        id = sanitize_id(id)
        u = await self._connection.api.users(id).get()

        u = User(self._connection, u)

        if cache:
            self._connection.store_user(u)

        return u

    async def fetch_guild(
        self,
        id: Id,
        *,
        fetch_members: bool = False,
        fetch_channels: bool = True,
        cache: bool = False,
    ) -> Guild:
        """|coro|

        Fetches a guild by ID.

        Parameters
        ----------
        id: int
            The guild's ID.
        fetch_members: Optional[bool], default False
            Whether to fetch the guild's members. Defaults to ``False``.
        fetch_channels: Optional[bool], default True
            Whether to fetch the guild's channels. Defaults to ``True``.
        cache: Optional[bool], default False
            Whether to cache the guild in the internal guild cache.

        Returns
        -------
        :class:`Guild`
            The guild fetched.

        Raises
        ------
        :exc:`NotFound`
            A guild with the given ID was not found.
        """
        id = sanitize_id(id)
        g = await self._connection.api.guilds(id).get(
            params={
                'members': str(fetch_members).lower(),
                'channels': str(fetch_channels).lower(),
            }
        )

        g = Guild(self._connection, g)

        if cache:
            self._connection.store_guild(g)

        return g

    async def close(self) -> None:
        if self.is_closed:
            return
        self._is_closed = True

        if hasattr(self, 'ws'):
            await self.ws.close(code=1000)

        if http := getattr(self._connection, '_http', None):
            if session := getattr(http, 'session', None):
                await session.close()

        self.dispatch('close')

    stop = close

    @overload
    async def start(self, *, token: str) -> None:
        ...

    @overload
    async def start(self, *, email: str, passsword: str, id: Id) -> None:
        ...

    async def start(
        self,
        token: Optional[str] = None,
        *,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """|coro|

        Establishes a websocket connection with FerrisChat's gateway.
        A form of authentication (email and password, or a token) must be provided.

        Parameters
        ----------
        token: Optional[str]
            The token used to authenticate.
        email: Optional[str]
            The email used to authenticate.
        password: Optional[str]
            The password used to authenticate.
        id: Optional[int]
            The ID of the guild to join.
        """

        if email is not None and password is not None and token is not None:
            raise ValueError('Cannot pass both email and password and token')

        if token is not None and (email is not None or password is not None):
            raise ValueError('Cannot pass both token and email or password')

        if token is None and (email is None or password is None):
            raise ValueError('Must pass either token or email and password')

        if token is not None:
            log.info("Logging in with Token")
            self._connection._initialize_http(token)
        else:
            log.info("Logging in with Email and Password")
            await self._connection._initialize_http_with_email(email, password)  # type: ignore

        self.dispatch('login')

        self.ws = Websocket(self)

        while not self.is_closed:
            try:
                await self.ws.connect()
            except Reconnect:
                del self.ws
                self.ws = Websocket(self)
                continue
            except WebsocketException:
                raise

    def run(self, *args, **kwargs) -> Any:
        """A helper function equivalent to

        .. code-block:: python3

            try:
                loop.run_until_complete(start(*args, **kwargs))
            except KeyboardInterrupt:
                loop.run_until_complete(_cancel_all_tasks())
            finally:
                loop.close()

        If you want finer control over the event loop, use :meth:`Client.start` instead.
        """
        # https://github.com/Rapptz/discord.py/blob/master/discord/client.py#L608 and
        # https://github.com/python/cpython/blob/main/Lib/asyncio/runners.py

        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.start(*args, **kwargs)
            finally:
                if not self.is_closed:
                    await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            log.info('Received signal to terminate bot and event loop')
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            log.info('Cleaning up tasks.')
            _cleanup_loop(loop)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                return None
