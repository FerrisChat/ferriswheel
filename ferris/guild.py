from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, cast

from .base import BaseObject

if TYPE_CHECKING:
    from .channel import Channel
    from .member import Member
    from .connection import Connection
    from .types import Data


__all__ = ('Guild',)


class Guild(BaseObject):
    """Represents a FerrisChat guild."""

    __slots__ = ('_connection', '_owner_id', '_name', '_channels', '_members')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        from .channel import Channel
        from .member import Member

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
        """|coro|

        Fetches a member from this guild.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def create_channel(self, name: str) -> Channel:
        """|coro|

        Creates a [text] channel in this guild.

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
        """|coro|

        Fetches a channel from this guild.

        Parameters
        ----------
        id: int
            The ID of the channel to fetch.

        Returns
        -------
        :class:`~.Channel`
        """
        c = await self._connection.api.guilds(self.id).channels(id).get()
        return Channel(self._connection, c)

    async def edit(self) -> None:
        """|coro|

        Edits this guild.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def delete(self) -> None:
        """|coro|

        Deletes this guild.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    def get_channel(self, id: int) -> Optional[Channel]:
        """Tries to retrieve a :class:`.~Channel` object
        given it's ID from the internal cache.

        Parameters
        ----------
        id: int
            The channel ID.

        Returns
        -------
        :class:`~.Channel`
            The channel found, if any.
        None
            The channel was not found in the internal cache.
        """
        return self._channels.get(id)

    def get_member(self, id: int) -> Optional[Member]:
        """Tries to retrieve a :class:`.~Member` object
        given it's ID from the internal cache.

        Parameters
        ----------
        id: int
            The member ID.

        Returns
        -------
        :class:`~.Member`
            The member foumd, if any.
        None
            The member was not found in the internal cache.
        """
        return self._members.get(id)

    @property
    def owner_id(self, /) -> int:
        """int: The ID of the owner of this guild."""
        return self._owner_id

    @property
    def name(self, /) -> str:
        """str: The name of this guild."""
        return self._name

    @property
    def channels(self, /) -> List[Channel]:
        """List[:class:`~.Channel`]: A list of all [cached] channels in this guild."""
        return list(self._channels.values())

    @property
    def members(self, /) -> List[Member]:
        """List[:class:`~.Member`]: A list of all [cached] members in this guild."""
        return list(self._members.values())

    def __repr__(self, /) -> str:
        return f'<Guild id={self.id} name={self.name!r}> owner_id={self.owner_id}'

    def __str__(self, /) -> str:
        return self.name
