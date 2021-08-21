from __future__ import annotations

from typing import cast, TYPE_CHECKING

from .base import BaseObject


if TYPE_CHECKING:
    from .message import Message
    from .connection import Connection
    from .types import Data

__all__ = ('Channel',)


class Channel(BaseObject):
    """
    Represents a channel in FerrisChat.
    """
    __slots__ = ('_connection', '_name')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)
        super().__init__()

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))

    async def fetch_message(self, message_id: int) -> Message:
        """
        |coro|

        Fetches a message from this channel.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    async def send(self) -> None:
        """
        |coro|

        Sends a message to this channel.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

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

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    @property
    def name(self, /) -> str:
        """str: The name of this channel."""
        return self._name
