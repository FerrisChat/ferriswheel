from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from datetime import datetime
from .utils import FERRIS_EPOCH

from .base import BaseObject

if TYPE_CHECKING:
    from .connection import Connection
    from .types import Snowflake
    from .types.invite import InvitePayload


class Invite:
    """
    Represents a invite to join guild.
    """
    def __init__(self, connection: Connection, payload: Optional[InvitePayload]):
        self._connection = connection
        self._process_data(payload)
    
    def _process_data(self, data: Optional[InvitePayload], /) -> None:
        if not data:
            return
        self._code: str = data.get('code')
        self._owner_id: Snowflake = data.get('owner_id')
        self._guild_id: Snowflake = data.get('guild_id')
        self._created_at: datetime = datetime.fromtimestamp((data.get('created_at', 0) + FERRIS_EPOCH))
        self._uses: int = data.get('uses')
        self._max_uses: int = data.get('max_uses')
        self._max_age: int = data.get('max_age')
    
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
    
    