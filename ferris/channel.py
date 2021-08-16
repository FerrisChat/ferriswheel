from typing import cast

from .base import BaseObject
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

    @property
    def name(self, /) -> str:
        return self._name
