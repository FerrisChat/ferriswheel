from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from .base import BaseObject


if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data, Snowflake
    from .types.message import MessagePayload
    from .channel import Channel
    from .user import User
    from .member import Member

__all__ = ('Message',)


class Message(BaseObject):
    """Represents a message from FerrisChat."""

    __slots__ = ('_connection', '_content', '_channel_id', '_author_id')

    def __init__(
        self, connection: Connection, data: Optional[MessagePayload], /
    ) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[MessagePayload], /) -> None:
        if not data:
            return

        self._store_snowflake(data.get('id'))

        self._content: Optional[str] = data.get('content')
        self._channel_id: Optional[Snowflake] = data.get('channel_id')

        self._author_id: Optional[Snowflake] = data.get('author_id')

    async def edit(self, content: str) -> Message:
        """|coro|

        Edits this message.

        Parameters
        ----------
        content: str
            The new content for this message.

        Returns
        -------
        Message
            The edited message.
        """
        payload = {'content': content}
        m = (
            await self._connection.api.channels(self.channel_id)
            .messages(self.id)
            .patch(payload)
        )
        self._process_data(m)
        return self

    async def delete(self) -> None:
        """|coro|

        Deletes this message.
        """
        await self._connection.api.channels(self.channel_id).messages(self.id).delete()

    @property
    def author(self, /) -> Optional[Union[Member, User]]:
        if self.channel and self.channel.guild:
            return self.channel.guild.get_member(
                self.author_id
            ) or self._connection.get_user(self.author_id)
        return self._connection.get_user(self.author_id)

    @property
    def channel(self, /) -> Optional[Channel]:
        """Channel: The channel that this message was sent in"""
        return self._connection.get_channel(self.channel_id)

    @property
    def author_id(self, /) -> Optional[Snowflake]:
        """int: Returns the author ID of this message."""
        return self._author_id

    @property
    def content(self, /) -> Optional[str]:
        """str: The content of this message."""
        return self._content

    @property
    def channel_id(self, /) -> Optional[Snowflake]:
        """int: The ID of the channel this message was sent in."""
        return self._channel_id

    def __repr__(self, /) -> str:
        return f'<Message id={self.id} author_id={self.author_id} channel_id={self.channel_id}>'
