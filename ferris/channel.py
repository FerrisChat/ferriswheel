from typing import cast

from .base import BaseObject
from .types import Data


class Channel(BaseObject):
    def __init__(self, data: Data) -> None:
        self._process_data(data)

    def _process_data(self, data: Data) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._name: str = cast(str, data.get('name'))
    
    @property
    def name(self) -> str:
        return self._name
