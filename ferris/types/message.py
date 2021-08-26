from typing import TypedDict

from .base import Snowflake


__all__ = ('MessagePayload',)


class MessagePayload(TypedDict):
    id: Snowflake
    content: str
    channel_id: Snowflake
    author_id: Snowflake
