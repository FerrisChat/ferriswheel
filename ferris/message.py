from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .base import BaseObject


if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data

__all__ = ('Message',)


class Message(BaseObject):
    """
    Represent a message from FerrisChat.
    """

    __slots__ = ('_connection', '_content', '_channel_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._content: str = cast(str, data.get('content'))
        self._channel_id: int = cast(int, data.get('channel_id'))

    async def edit(self) -> None:
        """
        |coro|

        Edit this message.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def delete(self) -> None:
        """
        |coro|

        Delete this message.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    @property
    def content(self, /) -> str:
        """str: The message's content"""
        return self._content

    @property
    def channel_id(self, /) -> int:
        """int: The channel's id"""
        return self._channel_id
