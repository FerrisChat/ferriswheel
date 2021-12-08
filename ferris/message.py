from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .base import BaseObject

if TYPE_CHECKING:
    from typing_extensions import Self
    from .channel import Channel
    from .connection import Connection
    from .guild import Guild
    from .user import User
    from .types import Data, Snowflake
    from .types.message import MessagePayload

__all__ = ('Message',)


class Message(BaseObject):
    """Represents a message from FerrisChat."""

    __slots__ = (
        '_connection',
        '_content',
        '_channel_id',
        '_author_id',
        '_author',
        '_edited_at',
    )

    def __init__(
        self, connection: Connection, data: Optional[MessagePayload], /
    ) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Optional[MessagePayload], /) -> None:
        if not data:
            data: dict = {}

        from .user import User

        self._store_snowflake(data.get('id'))

        self._content: Optional[str] = data.get('content')

        self._channel: Optional[Channel] = None

        if c := data.get('channel'):
            self._channel = Channel(self._connection, c)

        self._channel_id: Snowflake = data.get('channel_id')

        self._author_id: Snowflake = data.get('author_id')
        self._author: Optional[User] = User(self._connection, data.get('author'))

        self._edited_at: Optional[datetime] = None

        if edited_at := data.get('edited_at'):
            self._edited_at = datetime.fromisoformat(edited_at)

    async def edit(self, content: str) -> Self:
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
            .patch(json=payload)
        )
        self._process_data(m)
        return self

    async def delete(self) -> None:
        """|coro|

        Deletes this message.
        """
        await self._connection.api.channels(self.channel_id).messages(self.id).delete()

    @property
    def author(self, /) -> Optional[User]:
        """
        User: The author of this message.
        """
        return self._author

    @property
    def edited_at(self, /) -> Optional[datetime]:
        """datetime: The time at which this message was last edited."""
        return self._edited_at

    @property
    def channel(self, /) -> Optional[Channel]:
        """Channel: The channel that this message was sent in"""
        return self._cahnnel or self._connection.get_channel(self.channel_id)

    @property
    def channel_id(self, /) -> Snowflake:
        """Snowflake: The ID of the channel this message was sent in."""
        return self._channel_id

    @property
    def guild(self, /) -> Optional[Guild]:
        """Guild: The guild that this message was sent in"""
        return self.channel.guild

    @property
    def author_id(self, /) -> Snowflake:
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
