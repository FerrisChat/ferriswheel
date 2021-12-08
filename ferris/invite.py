from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from .utils import FERRIS_EPOCH


__all__ = ('Invite',)

if TYPE_CHECKING:
    from .connection import Connection
    from .guild import Guild
    from .member import Member
    from .types import Snowflake
    from .types.invite import InvitePayload
    from .user import User


class Invite:
    """
    Represents a invite to join guild.
    """

    __slots__ = (
        '_code',
        '_owner_id',
        '_guild_id',
        '_created_at',
        '_uses',
        '_max_uses',
        '_max_age',
        '_connection',
    )

    def __init__(self, connection: Connection, payload: Optional[InvitePayload]):
        self._connection = connection
        self._process_data(payload)

    def _process_data(self, data: Optional[InvitePayload], /) -> None:
        if not data:
            data: dict = {}

        self._code: str = data.get('code')
        self._owner_id: Snowflake = data.get('owner_id')
        self._guild_id: Snowflake = data.get('guild_id')
        try:
            self._created_at: Optional[datetime] = datetime.fromtimestamp(
                (data.get('created_at', 0) + FERRIS_EPOCH)
            )
        except OSError:
            self._created_at: Optional[
                datetime
            ] = None  # FIXME: When ferrischat fixes it.
        self._uses: int = data.get('uses')
        self._max_uses: int = data.get('max_uses')
        self._max_age: int = data.get('max_age')

    @property
    def owner(self, /) -> Optional[Union[Member, User]]:
        """Optional[Union[Member, User]]: The owner of this invite."""
        if self.guild:
            return self.guild.get_member(self.owner_id) or self._connection.get_user(
                self.owner_id
            )
        return self._connection.get_user(self.owner_id)

    @property
    def guild(self, /) -> Optional[Guild]:
        """Optional[Guild]: The guild of this invite."""
        return self._connection.get_guild(self.guild_id)

    @property
    def code(self) -> str:
        """str: The invite code."""
        return self._code

    @property
    def guild_id(self) -> Snowflake:
        """Snowflake: The guild id this invite is for."""
        return self._guild_id

    @property
    def created_at(self) -> datetime:
        """datetime: The time this invite was created."""
        return self._created_at

    @property
    def uses(self) -> int:
        """int: The number of times this invite has been used."""
        return self._uses

    @property
    def max_uses(self) -> int:
        """int: The maximum number of times this invite can be used."""
        return self._max_uses

    @property
    def max_age(self) -> int:
        """int: The maximum age of this invite."""
        return self._max_age

    def __repr__(self) -> str:
        return f'<Invite code={self.code!r} guild={self.guild_id} uses={self.uses} max_uses={self.max_uses} max_age={self.max_age}>'
