from datetime import datetime
from typing import Any

__all__ = ('to_json', 'from_json', 'get_snowflake_creation_date')

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

FERRIS_EPOCH = 1640995200000


if HAS_ORJSON:

    def to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')

    from_json = orjson.loads
else:

    def to_json(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=True)

    from_json = json.loads


def get_snowflake_creation_date(snowflake: int) -> datetime:
    seconds = (snowflake >> 64 + FERRIS_EPOCH) / 1000
    return datetime.utcfromtimestamp(seconds)
