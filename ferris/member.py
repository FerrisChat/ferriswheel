from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import BaseObject
from .user import User

if TYPE_CHECKING:
    from .guild import Guild
    from .connection import Connection
    from .types import Data
    from .types.member import MemberPayload

__all__ = ('Member',)


class Member(BaseObject):
    """Represents a member of a :class:`~.Guild`."""

    __slots__ = ('_connection', '_user', '_guild', '_guild_id')

    def __init__(self, connection: Connection, data: MemberPayload, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[MemberPayload], /) -> None:
        if not data:
            return

        self._store_snowflake(data.get('user_id'))

        self._user: Optional[User] = User(self._connection, data.get('user', {}))  # type: ignore
        self._connection.store_user(self._user)

        self._guild_id: Optional[int] = data.get('guild_id')

        from .guild import Guild

        self._guild: Optional[Guild] = Guild(self._connection, data.get('guild'))

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
    def user(self, /) -> Optional[User]:
        """:class:`~.User`: The user that belongs to this member."""
        return self._user

    @property
    def guild(self, /) -> Optional[Guild]:
        """:class:`~.Guild`: The guild that this member belongs to."""
        return self._guild

    @property
    def guild_id(self, /) -> Optional[int]:
        """int: The ID of the guild that this member belongs to."""
        return self._guild_id

    def __repr__(self, /) -> str:
        return f'<Member id={self.id} user={self.user!r} guild={self.guild!r}>'
