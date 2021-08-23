from datetime import datetime
from typing import Any, Callable, Iterable, Optional, TypeVar

from .types import Id, Snowflake

__all__ = ('to_json', 'from_json', 'get_snowflake_creation_date', 'find')

T = TypeVar('T', covariant=True)

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


def sanitize_id(id: Id) -> Snowflake:
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
    return getattr(id, 'id', id)


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
    seconds = (snowflake >> 64 + FERRIS_EPOCH) / 1000
    return datetime.utcfromtimestamp(seconds)


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
