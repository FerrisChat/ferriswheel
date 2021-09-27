from datetime import datetime
from typing import Any, Callable, Iterable, Optional, TypeVar

from .types import Id, Snowflake

__all__ = (
    'to_json',
    'from_json',
    'get_snowflake_creation_date',
    'find',
    'dt_to_snowflake',
)

T = TypeVar('T', covariant=True)

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

FERRIS_EPOCH_MS: int = 1_577_836_800_000


FERRIS_EPOCH: int = 1_577_836_800


if HAS_ORJSON:

    def to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')

    def from_json(json_str: str) -> Any:
        if not json_str:
            return None
        return orjson.loads(json_str)


else:

    def to_json(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=True)

    def from_json(json_str: str) -> Any:
        if not json_str:
            return None
        return json.loads(json_str)


def sanitize_id(id: Id = None) -> Snowflake:
    """Sanitizes an ID.

    Parameters
    ----------
    id: Id
        The ID to sanitize.

    Returns
    -------
    Snowflake
        The sanitized ID.
    """
    return getattr(id, 'id', id) if id else None


def get_snowflake_creation_date(snowflake: int) -> datetime:
    """Returns the creation timestamp of the given snowflake.

    Parameters
    ----------
    snowflake: int
        The snowflake to get the creation timestamp of.

    Returns
    -------
    :class:`datetime.datetime`
        The creation date of the snowflake.
    """
    seconds = ((snowflake >> 64) + FERRIS_EPOCH_MS) / 1000
    return datetime.utcfromtimestamp(seconds)


def dt_to_snowflake(dt: datetime) -> int:
    """Generates a random snowflake that was created on the given datetime.

    Parameters
    ----------
    dt: :class:`datetime.datetime`
        The target creation date of the snowflake to generate.

    Returns
    -------
    int
        The generated snowflake.
    """
    timestamp = dt.timestamp() * 1000 - FERRIS_EPOCH_MS
    return int(timestamp) << 64


def find(predicate: Callable[[T], Any], iterable: Iterable[T]) -> Optional[T]:
    """Finds the first element in the iterable that satisfies the predicate.

    Parameters
    ----------
    predicate: Callable[[Any], Any]
        The predicate to check each element against.
    Iterable: Iterable[Any]
        The iterable to search.

    Returns
    -------
    Any
        The first element in the iterable that satisfies the predicate.
        Can be None if no element satisfies the predicate.

    """
    for element in iterable:
        if predicate(element):
            return element
    return None
