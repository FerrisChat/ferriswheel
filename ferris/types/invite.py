from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Snowflake


class InvitePayload(TypedDict):
    code: str
    owner_id: Snowflake
    guild_id: Snowflake
    created_at: int
    uses: int
    max_uses: int
    max_age: int
