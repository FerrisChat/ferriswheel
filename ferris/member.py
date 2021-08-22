from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import BaseObject
from .user import User

if TYPE_CHECKING:
    from .guild import Guild
    from .connection import Connection
    from .types import Data

__all__ = ('Member',)


class Member(BaseObject):
    """Represents a member of a :class:`~.Guild`."""

    __slots__ = ('_connection', '_user', '_guild', '_guild_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)
        super().__init__()

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('user_id')))

        self._user: User = User(self._connection, cast(dict, data.get('user', {})))
        self._connection._store_user(self._user)

        self._guild_id: int = cast(int, data.get('guild_id'))
        from .guild import Guild

        self._guild: Guild = Guild(self._connection, cast(dict, data.get('guild', {})))

    async def edit(self) -> None:
        """|coro|

        Edits this member.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def delete(self) -> None:
        """|coro|

        Kicks this member from it's guild.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    @property
    def user(self, /) -> User:
        """:class:`~.User`: The user that belongs to this member."""
        return self._user

    @property
    def guild(self, /) -> Guild:
        """:class:`~.Guild`: The guild that this member belongs to."""
        return self._guild

    @property
    def guild_id(self, /) -> int:
        """int: The ID of the guild that this member belongs to."""
        return self._guild_id

    def __repr__(self, /) -> str:
        return f'<Member id={self.id} user={self.user!r} guild={self.guild!r}>'
