from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, Dict

from .types.base import Id

from .base import BaseObject
from .user import User

if TYPE_CHECKING:
    from .role import Role
    from .guild import Guild
    from .connection import Connection
    from .types import Data
    from .types.member import MemberPayload
    from .types import Snowflake

__all__ = ('Member',)


class Member(BaseObject):
    """Represents a member of a :class:`~.Guild`."""

    __slots__ = ('_connection', '_user', '_guild', '_guild_id', '_roles')

    def __init__(self, connection: Connection, data: MemberPayload, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[MemberPayload], /) -> None:
        if not data:
            data: dict = {}

        self._store_snowflake(data.get('user_id'))

        if user := self._connection.get_user(self.id):
            self._user = user
            self._user._process_data(data.get('user') or {})
        else:
            self._user: Optional[User] = User(self._connection, data.get('user') or {})  # type: ignore
            self._connection.store_user(self._user)

        self._guild_id: Optional[Snowflake] = data.get('guild_id')

        if guild := self._connection.get_guild(self._guild_id):
            guild._process_data(data.get('guild') or {})
        else:

            from .guild import Guild

            guild: Optional[Guild] = Guild(
                self._connection, data.get('guild', {}) or {}
            )

            self._connection.store_guild(guild)

        self._guild: Optional[Guild] = guild

        self._roles: Dict[Snowflake, Role] = {}

    async def add_role(self, role: Union[Role, Id]) -> None:
        """|coro|

        Adds a role to this member.

        Parameters
        ----------
        role: :class:`~.Role` or :class:`~.Snowflake`
            The role to add to this member.
        """
        await self._connection.api.guilds(self.guild_id).members(self.id).roles(
            role.id
        ).post()

    async def remove_role(self, role: Union[Role, Id]) -> None:
        """|coro|

        Removes a role from this member.

        Parameters
        ----------
        role: :class:`~.Role` or :class:`~.Snowflake`
            The role to remove from this member.
        """
        await self._connection.api.guilds(self.guild_id).members(self.id).roles(
            role.id
        ).delete()

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
