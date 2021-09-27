from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, cast

from .base import BaseObject
from .utils import sanitize_id
from .channel import Channel

if TYPE_CHECKING:
    from .member import Member
    from .connection import Connection
    from .types import Data, Id, Snowflake
    from .types import GuildPayload, ChannelPayload
    from ferris.invite import Invite


__all__ = ('Guild',)


class Guild(BaseObject):
    """Represents a FerrisChat guild."""

    __slots__ = ('_connection', '_owner_id', '_name', '_channels', '_members')

    def __init__(self, connection: Connection, data: Optional[GuildPayload], /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[GuildPayload], /) -> None:
        if not data:
            return

        from .member import Member

        self._store_snowflake(data.get('id'))

        self._owner_id: Optional[int] = data.get('owner_id')
        self._name: Optional[str] = data.get('name')

        self._channels: Dict[int, Channel] = {}

        for c in data.get('channels') or []:
            if channel := self._connection.get_channel(c.get('id')):
                channel._process_data(c)
            else:
                channel = Channel(self._connection, c)
            self._channels[channel.id] = channel

        self._members: Dict[int, Member] = {}

        for m in data.get('members') or []:
            member = Member(self._connection, m)
            self._members[member.id] = member

    async def fetch_member(self, id: Id) -> Member:
        """|coro|

        Fetches a member from this guild.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def fetch_invites(self) -> List[Invite]:
        """|coro|

        Fetches all the invites for this guild.

        Returns
        -------
        List[:class:`~.Invite`]
        """
        invites = await self._connection.api.guilds(self.id).invites.get()
        return [Invite(self._connection, i) for i in invites]

    async def create_invite(self, max_age: int = None, max_uses: int = None) -> Invite:
        """|coro|

        Creates an invite for this guild.

        Parameters
        ----------
        max_age: Optional[int]
            The maximum age of the invite, in seconds.
        max_uses: Optional[int]
            The maximum uses of the invite.

        Returns
        -------
        :class:`~.Invite`
        """
        payload = {
            'max_age': max_age,
            'max_uses': max_uses,
        }
        invite = await self._connection.api.guilds(self.id).invites.post(json=payload)
        return Invite(self._connection, invite)

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
        c: ChannelPayload = await self._connection.api.guilds(self.id).channels.post(
            json={'name': name}
        )
        return Channel(self._connection, c)

    async def fetch_channel(self, id: Id) -> Channel:
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
        id = sanitize_id(id)
        c = await self._connection.api.guilds(self.id).channels(id).get()
        return Channel(self._connection, c)

    async def edit(self, name: str) -> Guild:
        """|coro|

        Edits this guild.

        Parameters
        ----------
        name: str
            The new name of the guild.

        Returns
        -------
        :class:`~.Guild`
        """
        payload = {name: name}
        guild = await self._connection.api.guilds(self.id).patch(json=payload)
        self._process_data(guild)
        return self

    async def delete(self) -> None:
        """|coro|

        Deletes this guild.
        """
        await self._connection.api.guilds(self.id).delete()

    def get_channel(self, id: Id) -> Optional[Channel]:
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
        id = sanitize_id(id)
        return self._channels.get(id)

    def get_member(self, id: Id) -> Optional[Member]:
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
        id = sanitize_id(id)
        return self._members.get(id)

    @property
    def owner(self) -> Optional[Member]:
        """Member: The owner of this guild."""
        return self.get_member(self._owner_id)

    @property
    def owner_id(self, /) -> Optional[Snowflake]:
        """int: The ID of the owner of this guild."""
        return self._owner_id

    @property
    def name(self, /) -> Optional[str]:
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
        return self.name or self.__repr__()
