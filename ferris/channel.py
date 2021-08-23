from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import BaseObject
from .message import Message
from .utils import sanitize_id

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data, Snowflake, Id

__all__ = ('Channel',)


class Channel(BaseObject):
    """
    Represents a channel in FerrisChat.
    """

    __slots__ = ('_connection', '_name', '_guild_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))

        self._guild_id: int = cast(int, data.get('guild_id'))

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

    async def send(self, content: str) -> None:
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
        m = (
            await self._connection.api.guilds(self.guild_id)
            .channels(self.id)
            .messages.post(json={'content': content})
        )
        return Message(self._connection, m)

    async def edit(self) -> None:
        """
        |coro|

        Edits this channel.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def delete(self) -> None:
        """
        |coro|

        Deletes this channel.
        """
        await self._connection.api.channels(self.id).delete()

    @property
    def guild_id(self) -> Snowflake:
        """int: The ID of the guild this channel belongs to."""
        return self._guild_id

    @property
    def name(self, /) -> str:
        """str: The name of this channel."""
        return self._name

    def __del__(self, /) -> None:
        if not hasattr(self, '_connection'):
            return

        self._connection.deref_channel(self.id)
