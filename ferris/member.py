from typing import cast

from .base import BaseObject
from .connection import Connection
from .guild import Guild
from .types import Data
from .user import User

__all__ = ('Member',)


class Member(BaseObject):
    """
    Represents a member of a FerrisChat guild.
    """

    __slots__ = ('_connection', '_user', '_guild', '_guild_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('user_id')))

        self._user: User = User(self._connection, cast(dict, data.get('user', {})))
        self._connection._store_user(self._user)

        self._guild_id: int = cast(int, data.get('guild_id'))
        self._guild: Guild = Guild(self._connection, cast(dict, data.get('guild', {})))
    
    async def edit(self) -> None:
        """
        |coro|

        Edits the member.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...
    
    async def delete(self) -> None:
        """
        |coro|

        Deletes the member from the guild.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...

    @property
    def user(self, /) -> User:
        """:class:`~.User`: The user that belongs to the member."""
        return self._user

    @property
    def guild(self, /) -> Guild:
        """:class:`~.Guild`: The guild that the member belongs to."""
        return self._guild

    @property
    def guild_id(self, /) -> int:
        """int: The guild id that the member belongs to."""
        return self._guild_id

    def __repr__(self, /) -> str:
        return f'<Member id={self.id} user={self.user!r} guild={self.guild!r}>'
