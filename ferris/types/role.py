from typing import TypedDict

from .base import Snowflake


__all__ = ('RolePayload',)


class RolePayload(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    color: int
    position: int
    permissions: int
