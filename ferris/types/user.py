from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, List

if TYPE_CHECKING:
    from .base import Snowflake
    from .guild import GuildPayload


__all__ = ('UserPayload',)


class UserPayload(TypedDict):
    id: Snowflake
    name: str
    guilds: List[GuildPayload]
    flags: int
    avatar: str
