from __future__ import annotations
from ferris.types.base import Snowflake

from typing import TYPE_CHECKING, Dict, List, Optional

from .base import BaseObject
from .guild import Guild

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Data
    from .types.user import UserPayload

__all__ = ('PartialUser', 'User')


class PartialUser(BaseObject):
    """
    Represents a Partial FerrisChat User.
    """

    __slots__ = ('_name',)

    def __init__(self, data: Optional[UserPayload], /) -> None:
        self._process_data(data)

    def _process_data(self, data: Optional[UserPayload]) -> None:
        if not data:
            return

        self._store_snowflake(data.get('id'))

        self._name: Optional[str] = data.get('name')

    @property
    def name(self) -> Optional[str]:
        """str: The user's name."""
        return self._name

    def __repr__(self) -> str:
        return f'<PartialUser id={self.id} name={self.name!r}>'


class User(BaseObject):
    """
    Represents a FerrisChat user.
    """

    __slots__ = ('_connection', '_name', '_guilds', '_avatar')

    def __init__(self, connection: Connection, data: UserPayload, /) -> None:
        self._connection: Connection = connection
        self._process_data(data)

    def _process_data(self, data: UserPayload, /) -> None:
        self._store_snowflake(data.get('id'))

        self._name: Optional[str] = data.get('name')

        self._avatar: Optional[str] = data.get('avatar')

        self._guilds: Dict[int, Guild] = {}

        for g in data.get('guilds') or []:
            guild_id = g.get('id')

            if guild_id in self._guilds:
                guild = self._connection.get_guild(guild_id)
                guild._process_data(g)

            if guild_id not in self._guilds:
                guild = Guild(self._connection, g)
                self._connection.store_guild(guild)

            self._guilds[guild_id] = self._connection.get_guild(guild_id)

        # self._flags = data.get('flags')
        # UserFlag after ferrischat implemented it

    async def edit(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """|coro|

        Edits the user.

        Parameters
        ----------
        username : Optional[str]
            The new username.
        email : Optional[str]
            The new email.
        password : Optional[str]
            The new password.

        Returns
        -------
        User
            The edited user.
        """
        payload = {
            'username': username,
            'email': email,
            'password': password,
        }
        user = await self._connection.api.users(self.id).patch(payload)
        self._process_data(user)
        return self

    async def fetch_guilds(self) -> List[Guild]:
        """|coro|

        Fetches all the guilds this user is in.

        Returns
        -------
        List[:class:`~.Guild`]
            A list of the guilds this user is in.

        .. warning::
            This method will do nothing as FerrisChat has not implemented this feature yet.
        """
        ...

    @property
    def name(self, /) -> Optional[str]:
        """str: The username of this user."""
        return self._name

    @property
    def guilds(self, /) -> List[Guild]:
        """List[:class:`~.Guild`]: A list of the guilds this user is in."""
        return list(self._guilds.values())

    @property
    def avatar(self, /) -> Optional[str]:
        """str: The avatar url of this user."""
        return self._avatar

    def __del__(self, /) -> None:
        if not hasattr(self, '_connection'):
            return

        self._connection.deref_user(self.id)

    def __repr__(self, /) -> str:
        return f'<User id={self.id} name={self.name!r}>'
