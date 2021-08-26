from __future__ import annotations

from typing import TypedDict, List, TYPE_CHECKING


if TYPE_CHECKING:
    from .base import Snowflake
    from .channel import ChannelPayload
    from .member import MemberPayload


__all__ = ('GuildPayload',)


class GuildPayload(TypedDict):
    id: Snowflake
    owner_id: Snowflake
    name: str
    channels: List[ChannelPayload]
    members: List[MemberPayload]
