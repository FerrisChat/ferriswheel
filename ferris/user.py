from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, cast

from .base import BaseObject
from .guild import Guild

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data

__all__ = ('PartialUser', 'User')


class PartialUser(BaseObject):
    """
    Represents a Partial FerrisChat User.
    """

    __slots__ = ('_name',)

    def __init__(self, data: Data, /) -> None:
        self._process_data(data)

    def _process_data(self, data: Data) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name = data.get('name')

    @property
    def name(self) -> str:
        """str: The user's name."""
        return self._name


class User(BaseObject):
    """
    Represents a FerrisChat user.
    """

    __slots__ = ('_connection', '_name', '_guilds')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))

        self._guilds: Dict[int, Guild] = {}

        for g in data.get('guilds') or []:
            guild = Guild(self._connection, g)
            self._guilds[guild.id] = guild

        # self._flags = data.get('flags')
        # UserFlag after ferrischat implemented it

    async def fetch_guilds(self) -> List[Guild]:
        """|coro|

        Fetches all the guilds this user is in.

        Returns
        -------
        List[:class:`~.Guild`]
            A list of the guilds this user is in.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    @property
    def name(self, /) -> str:
        """str: The username of this user."""
        return self._name

    @property
    def guilds(self, /) -> List[Guild]:
        """List[:class:`~.Guild`]: A list of the guilds this user is in."""
        return list(self._guilds.values())

    def __del__(self, /) -> None:
        if not hasattr(self, '_connection'):
            return

        self._connection.deref_user(self.id)

    def __expr__(self, /) -> str:
        return f'<User id={self.id} name={self.name!r}>'
