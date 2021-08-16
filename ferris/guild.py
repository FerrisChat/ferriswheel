from typing import Dict, List, cast

from .base import BaseObject
from .connection import Connection
from .channel import Channel
from .member import Member
from .types import Data

__all__ = ('Guild',)


class Guild(BaseObject):

    __slots__ = ('_connection', '_owner_id', '_name', '_channels', '_members')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('id')))

        self._owner_id: int = cast(int, data.get('owner_id'))
        self._name: str = cast(str, data.get('name'))

        self._channels: Dict[int, Channel] = {}

        for c in data.get('channels', []):
            channel = Channel(self._connection, c)
            self._channels[channel.id] = channel

        self._members: Dict[int, Member] = {}

        for m in data.get('members', []):
            member = Member(self._connection, m)
            self._members[member.id] = member

    @property
    def owner_id(self, /) -> int:
        return self._owner_id

    @property
    def name(self, /) -> str:
        return self._name

    @property
    def channels(self, /) -> List[Channel]:
        return list(self._channels.values())

    @property
    def members(self, /) -> List[Member]:
        return list(self._members.values())

    def __repr__(self, /) -> str:
        return f'<Guild id={self.id} name={self.name!r}> owner_id={self.owner_id}'

    def __str__(self, /) -> str:
        return self.name
