from typing import TypedDict

from .base import Snowflake

__all__ = ('ChannelPayload',)


class ChannelPayload(TypedDict):
    id: Snowflake
    name: str
    guild_id: Snowflake
