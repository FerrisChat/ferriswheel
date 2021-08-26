from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .base import Snowflake
    from .user import UserPayload
    from .guild import GuildPayload

__all__ = ('MemberPayload',)


class MemberPayload(TypedDict):
    user_id: Snowflake
    user: UserPayload
    guild: GuildPayload
    guild_id: Snowflake
