from typing import cast

from .types import Data
from .base import BaseObject
from .connection import Connection

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

    @property
    def content(self, /) -> str:
        return self._content

    @property
    def channel_id(self, /) -> int:
        return self._channel_id
