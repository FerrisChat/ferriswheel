from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, cast

from .base import BaseObject
from .channel import Channel
from .member import Member

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data


__all__ = ('Guild',)


class Guild(BaseObject):
    """
    Represents a FerrisChat guild.
    """

    __slots__ = ('_connection', '_owner_id', '_name', '_channels', '_members')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._owner_id: int = cast(int, data.get('owner_id'))
        self._name: str = cast(str, data.get('name'))

        self._channels: Dict[int, Channel] = {}

        for c in data.get('channels', []):
            channel = Channel(self._connection, c)
            self._channels[channel.id] = channel

        self._members: Dict[int, Member] = {}

        for m in data.get('members', []):
            member = Member(self._connection, m)
            self._members[member.id] = member

    async def fetch_member(self, id: int) -> Member:
        """
        |coro|

        Fetch a member from the guild.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def create_channel(self, name: str) -> Channel:
        """
        |coro|

        Creates a channel in the guild.

        Parameters
        ----------
        name: str
            The name of the channel.

        Returns
        -------
        :class:`~.Channel`

        """
        c = await self._connection.api.guilds(self.id).channels.post(
            json={'name': name}
        )
        return Channel(self._connection, c)

    async def fetch_channel(self, id: int) -> Channel:
        """
        |coro|

        Fetch a channel from the guild.

        Parameters
        ----------
        id: int
            The channel ID.

        Returns
        -------
        :class:`~.Channel`
        """
        c = await self._connection.api.guilds(self.id).channels(id).get()
        return Channel(self._connection, c)

    async def edit(self) -> None:
        """|coro|

        Edits the guild.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def delete(self) -> None:
        """|coro|

        Deletes the guild.

        .. warning::
            This method does nothing as ferrischat haven't implemented it yet.
        """
        ...

    def get_channel(self, id: int) -> Optional[Channel]:
        """
        Returns the channel with the given ID.

        Parameters
        ----------
        id: int
            The channel ID.

        Returns
        -------
        :class:`~.Channel`
        """
        return self._channels.get(id)

    def get_member(self, id: int) -> Optional[Member]:
        """
        Returns the member with the given ID.

        Parameters
        ----------
        id: int
            The member ID.

        Returns
        -------
        :class:`~.Member`
        """
        return self._members.get(id)

    @property
    def owner_id(self, /) -> int:
        """int: The guild owner's ID."""
        return self._owner_id

    @property
    def name(self, /) -> str:
        """str: The guild's name."""
        return self._name

    @property
    def channels(self, /) -> List[Channel]:
        """List[:class:`~.Channel`]: A list of channels in the guild."""
        return list(self._channels.values())

    @property
    def members(self, /) -> List[Member]:
        """List[:class:`~.Member`]: A list of members in the guild."""
        return list(self._members.values())

    def __repr__(self, /) -> str:
        return f'<Guild id={self.id} name={self.name!r}> owner_id={self.owner_id}'

    def __str__(self, /) -> str:
        return self.name
