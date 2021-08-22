from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, overload, Optional, Dict, List, Awaitable

from .connection import Connection
from .guild import Guild
from .user import User
from .channel import Channel
from .message import Message

__all__ = ('Dispatcher', 'Client')


class Dispatcher:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop: asyncio.AbstractEventLoop = loop
        self.event_handlers: Dict[str, List[Awaitable]] = {}

    def dispatch(self, event: str, *args) -> None:
        if event not in self.event_handlers:
            return

        for handler in self.event_handlers[event]:
            self.loop.create_task(handler(*args))


class Client(Dispatcher):
    """Represents a client connection to FerrisChat.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The event loop to use for the client. If not passed, then the default event loop is used.

    max_messages_count: Optional[int]
        The maximum number of messages to store in the internal message buffer.
        Defaults to ``1000``.
    """

    __slots__ = ('loop', 'api', '_connection')

    def __init__(self, /, loop: asyncio.AbstractEventLoop = None, **options) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self._connection: Connection = Connection(self.loop, **options)
        super().__init__(loop)

    def _initialize_connection(self, token: str, /) -> None:
        self._connection._initialize_http(token)

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

    def get_message(self, id: int) -> Optional[Message]:
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
        return self._connection.get_message(id)

    def get_channel(self, id: int) -> Optional[Channel]:
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
        return self._connection.get_channel(id)

    def get_user(self, id: int) -> Optional[User]:
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
        return self._connection.get_user(id)

    async def fetch_message(self, id: int) -> Message:
        """|coro|

        Fetches a message from the internal message buffer.

        Parameters
        ----------
        id: int
            The ID of the message to fetch.

        Returns
        -------
        :class:`Message`
            The message with the given ID.
        """
        m = await self._connection.api.messages(id).get()
        return Message(self._connection, m)

    async def fetch_channel(self, id: int) -> Channel:
        """|coro|

        Fetches a channel by ID.

        Parameters
        ----------
        id: int
            The ID of the channel to fetch.

        Returns
        -------
        :class:`Channel`
            The channel with the given ID.
        """
        c = await self._connection.api.channels(id).get()
        return Channel(self._connection, c)

    async def fetch_user(self, id: int) -> User:
        """|coro|

        Fetches a user by ID.

        Parameters
        ----------
        id: int
            The ID of the user to fetch.

        Returns
        -------
        :class:`User`
            The user with the given ID.
        """
        u = await self._connection.api.users(id).get()
        return User(self._connection, u)

    async def fetch_guild(
        self, id: int, fetch_members: bool = False, fetch_channels: bool = True
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

        Returns
        -------
        :class:`Guild`
            The guild fetched.

        Raises
        ------
        :exc:`NotFound`
            A guild with the given ID was not found.
        """
        g = await self._connection.api.guilds(id).get(
            params={'members': fetch_members, 'channels': fetch_channels}
        )
        return Guild(self._connection, g)

    @overload
    async def start(self, token: str) -> None:
        ...

    @overload
    async def start(self, email: str, passsword: str, id: int) -> None:
        ...

    async def start(
        self, token: str = None, email: str = None, password: str = None, id: int = None
    ) -> None:
        """|coro|

        Establishes a websocket connection with FerrisChat's gateway.
        A form of authentication (email and password, or a token) must be provided.

        The `id` kwarg is only needed when an email and password is used to login.

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

        if token is None and (email is None or password is None or id is None):
            raise ValueError('Must pass either token or email and password and id')

        if token is not None:
            self._initialize_connection(token)
        else:
            await self._connection._initialize_http_with_email(email, password, id)

    def run(self, *args, **kwargs):
        """A helper function equivalent to

        .. code-block:: python3

            asyncio.run(self.start, *args, **kwargs)

        If you want finer control over the event loop, use :meth:`Client.start` instead.
        """
        asyncio.run(self.start(*args, **kwargs))
