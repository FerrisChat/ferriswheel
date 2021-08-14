from typing import List, cast, Any

from .base import BaseObject
from .channel import Channel
from .member import Member
from .types import Data


class Guild(BaseObject):
    def __init__(self, data: Data) -> None:
        self._process_data(data)

    def _process_data(self, data: Data) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._owner_id: int = cast(int, data.get('owner_id'))
        self._name: str = cast(str, data.get('name'))

        self._channels: List[Channel] = [
            Channel(c) for c in cast(dict, data.get('channels', {}))
        ]

        self._members: List[Member] = [
            Member(m) for m in cast(dict, data.get('members', {}))
        ]
    
    @property
    def owner_id(self) -> int:
        return self._owner_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def channels(self) -> List[Channel]:
        return self._channels
    
    @property
    def members(self) -> List[Member]:
        return self._members
    
    def __repr__(self) -> str:
        return f'<Guild id={self.id} name={self.name!r}> owner_id={self.owner_id}'
    
    def __str__(self) -> str:
        return self.name
