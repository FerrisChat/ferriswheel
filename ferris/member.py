from typing import cast

from .base import BaseObject
from .connection import Connection
from .guild import Guild
from .types import Data
from .user import User

__all__ = ('Member',)


class Member(BaseObject):

    __slots__ = ('_connection', '_user', '_guild', '_guild_id')

    def __init__(self, connection: Connection, data: Data, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: Data, /) -> None:
        self._store_snowflake(cast(int, data.get('user_id')))

        self._user: User = User(self._connection, cast(dict, data.get('user', {})))
        self._connection._store_user(self._user)

        self._guild_id: int = cast(int, data.get('guild_id'))
        self._guild: Guild = Guild(self._connection, cast(dict, data.get('guild', {})))

    @property
    def user(self, /) -> User:
        return self._user

    @property
    def guild(self, /) -> Guild:
        return self._guild

    @property
    def guild_id(self, /) -> int:
        return self._guild_id

    def __repr__(self, /) -> str:
        return f'<Member id={self.id} user={self.user!r} guild={self.guild!r}>'
