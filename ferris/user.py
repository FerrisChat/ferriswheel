from typing import Dict, List, cast

from .base import BaseObject
from .connection import Connection
from .guild import Guild
from .types import Data

__all__ = ('User',)


class User(BaseObject):
    """
    Represents a FerrisChat user.
    """

    __slots__ = ('_connection', '_name', '_guilds', '_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))

        self._guilds: Dict[int, Guild] = {}

        for g in data.get('guilds', []):
            guild = Guild(self._connection, g)
            self._guilds[guild.id] = guild

        # self._flags = data.get('flags')
        # UserFlag after ferrischat implemented it

    async def fetch_guilds(self) -> List[Guild]:
        """|coro|

        Fetches all the guilds the user is in.

        Returns
        -------
        List[:class:`~.Guild`]
            A list of the guilds the user is in.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...

    @property
    def name(self, /) -> str:
        """str: The user's username."""
        return self._name

    @property
    def guilds(self, /) -> List[Guild]:
        """List[:class:`~.Guild`]: A list of the guilds the user is in."""
        return list(self._guilds.values())

    def __expr__(self, /) -> str:
        return f'<User id={self.id} name={self.name!r}>'
