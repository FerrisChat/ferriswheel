from __future__ import annotations

from typing import cast, TYPE_CHECKING

from .base import BaseObject


if TYPE_CHECKING:
    from .message import Message
    from .connection import Connection
    from .types import Data

__all__ = ('Channel',)


class Channel(BaseObject):

    __slots__ = ('_connection', '_name')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))

    async def fetch_message(self, message_id: int) -> Message:
        """
        |coro|

        Fetches a message from the channel.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def send(self) -> None:
        """
        |coro|

        Sends a message to the channel.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def edit(self) -> None:
        """
        |coro|

        Edits the channel.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    async def delete(self) -> None:
        """
        |coro|

        Deletes the channel.

        .. warning::
            This method do nothing as ferrischat haven't implemented it yet.
        """
        ...

    @property
    def name(self, /) -> str:
        return self._name
