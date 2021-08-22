from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import BaseObject


if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data

__all__ = ('Message',)


class Message(BaseObject):
    """Represents a message from FerrisChat."""

    __slots__ = ('_connection', '_content', '_channel_id', '_author_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)
        super().__init__()

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._content: str = cast(str, data.get('content'))
        self._channel_id: int = cast(int, data.get('channel_id'))

        self._author_id: int = cast(int, data.get('author_id'))


    async def edit(self) -> None:
        """|coro|

        Edits this message.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def delete(self) -> None:
        """|coro|

        Deletes this message.
        """
        await self._connection.api.messages(self.id).delete()
    
    @property
    def author_id(self, /) -> int:
        """int: Returns the author ID of this message."""
        return self._author_id

    @property
    def content(self, /) -> str:
        """str: The content of this message."""
        return self._content

    @property
    def channel_id(self, /) -> int:
        """int: The ID of the channel this message was sent in."""
        return self._channel_id
