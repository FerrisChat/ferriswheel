from datetime import datetime
from typing import Any

__all__ = ('to_json', 'from_json', 'get_snowflake_creation_date')

try:
    import orjson

    HAS_ORJSON: bool = True
except ImportError:
    import json

    HAS_ORJSON: bool = False

FERRIS_EPOCH: int = 1_577_836_800_000


if HAS_ORJSON:

    def to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')

    from_json = orjson.loads
else:

    def to_json(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=True)

    from_json = json.loads


def get_snowflake_creation_date(snowflake: int) -> datetime:
    """
    Returns the creation date of a snowflake.

    Parameters
    ----------
    snowflake: int
        The snowflake to get the creation date of.

    Returns
    -------
    datetime
        The creation date of the snowflake.
    """
    seconds = (snowflake >> 64 + FERRIS_EPOCH) / 1000
    return datetime.utcfromtimestamp(seconds)
