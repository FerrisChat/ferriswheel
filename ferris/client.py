from __future__ import annotations

import asyncio
from typing import overload, TYPE_CHECKING

from .connection import Connection


if TYPE_CHECKING:
    from .guild import Guild


__all__ = ('Client',)


class Client:
    """Represents a client connection to FerrisChat.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The event loop to use for the client. If not passed, then the default event loop is used.

    max_messages_count: Optional[int]
        The maximum number of messages to store in the internal message buffer.
        This Defaults to ``1000``.
    """

    __slots__ = ('loop', 'api', '_connection')

    def __init__(self, /, loop: asyncio.AbstractEventLoop = None, **options) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self._connection: Connection = Connection(self.loop, **options)

    def _initialize_connection(self, token: str, /) -> None:
        self._connection._initialize_http(token)

    async def create_guild(self, name: str) -> Guild:
        """
        |coro|

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

    async def fetch_guild(self, id: int) -> Guild:
        """
        |coro|

        Fetches a guild by ID.

        Parameters
        ----------
        id: int
            The guild's ID.

        Returns
        -------
        :class:`Guild`
            The guild.
        """
        g = await self._connection.api.guilds(id).get()
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
        """
        |coro|

        Connects to FerrisChat. You must pass in either token or email and password and id.
        Id is only needed when using email and password to login.

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
        """
        A helper function Equivalent to
        .. code-block: python3
            asyncio.run(self.start, *args, **kwargs)
        """
        asyncio.run(self.start(), *args, **kwargs)
