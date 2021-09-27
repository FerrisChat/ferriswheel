from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from .base import BaseObject
from .message import Message
from .utils import sanitize_id

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data, Snowflake, Id
    from .types.channel import ChannelPayload
    from .guild import Guild

__all__ = ('Channel',)


class Channel(BaseObject):
    """
    Represents a channel in FerrisChat.
    """

    __slots__ = ('_connection', '_name', '_guild_id')

    def __init__(
        self, connection: Connection, data: Optional[ChannelPayload], /
    ) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[ChannelPayload], /) -> None:
        if not data:
            return

        self._store_snowflake(data.get('id'))

        self._name: Optional[str] = data.get('name')

        self._guild_id: Optional[Snowflake] = data.get('guild_id')

    async def fetch_message(self, message_id: Id) -> Message:
        """
        |coro|

        Fetches a message from this channel.

        Parameters
        ----------
        message_id: int
            The ID of the message to fetch.

        Returns
        -------
        Message
        """
        message_id = sanitize_id(message_id)
        m = await self._connection.api.messages(message_id).get()
        return Message(self._connection, m)

    async def send(self, content: str) -> Message:
        """
        |coro|

        Sends a message to this channel.

        Parameters
        ----------
        content: str
            The content of the message.

        Returns
        -------
        Message
            The message that was sent.
        """
        m = await self._connection.api.channels(self.id).messages.post(
            json={'content': content}
        )
        return Message(self._connection, m)

    async def fetch_messages(self, limit: int = 100) -> List[Message]:
        """
        |coro|

        Fetches messages from this channel.

        Parameters
        ----------
        limit: int
            The maximum number of messages to fetch.
            Defaults to 100.
            Set it to 9223372036854775807 to fetch all messages.

        Returns
        -------
        List[Message]
        """
        data = await self._connection.api.channels(self.id).messages.get(limit=limit)
        return [Message(self._connection, m) for m in data]

    async def edit(self, name: str) -> Channel:
        """
        |coro|

        Edits this channel.

        Parameters
        ----------
        name: str
            The new name of the channel.

        Returns
        -------
        Channel
            The channel that was edited.
        """
        data = {'name': name}
        c = await self._connection.api.channels(self.id).patch(json=data)
        self._process_data(c)
        return self

    async def delete(self) -> None:
        """
        |coro|

        Deletes this channel.
        """
        await self._connection.api.channels(self.id).delete()

    @property
    def guild(self, /) -> Optional[Guild]:
        """Guild: The guild that this channel belongs to."""
        return self._connection.get_guild(self._guild_id)

    @property
    def guild_id(self) -> Optional[Snowflake]:
        """int: The ID of the guild this channel belongs to."""
        return self._guild_id

    @property
    def name(self, /) -> Optional[str]:
        """str: The name of this channel."""
        return self._name

    def __repr__(self, /) -> str:
        return f'<Channel id={self.id} name={self.name} guild_id={self.guild_id}>'

    def __del__(self, /) -> None:
        if not hasattr(self, '_connection'):
            return

        self._connection.deref_channel(self.id)
