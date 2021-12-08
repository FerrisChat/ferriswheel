from __future__ import annotations

import asyncio
import functools
import inspect
import sys
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec('P')

    T = TypeVar('T')
    R = TypeVar('R')
    TR = Callable[[T], Awaitable[R]]
    PT = Callable[[P], T]  # type: ignore
    A = Callable[[P], Awaitable[R]]  # type: ignore
    F = Callable[[P], R]  # type: ignore

from .types import Id, Snowflake

__all__ = (
    'to_json',
    'from_json',
    'get_snowflake_creation_date',
    'find',
    'dt_to_snowflake',
)


# try:
#     import orjson

#     HAS_ORJSON = True
# except ImportError:
#     import json


import json

HAS_ORJSON = False

FERRIS_EPOCH_MS: int = 1_577_836_800_000


FERRIS_EPOCH: int = 1_577_836_800

PY_3_8 = sys.version_info < (3, 9)


# if HAS_ORJSON:

#     def to_json(obj: Any) -> str:
#         return orjson.dumps(obj).decode('utf-8')

#     def from_json(json_str: str) -> Any:
#         if not json_str:
#             return None
#         return orjson.loads(json_str)


# else:


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


def pending(f: PT) -> PT:
    warning_text: str = """
.. warning::
This method is a pending feature, is not currently usable as FerrisChat have not implemented it yet but it will be soon."""

    f.__doc__ += warning_text

    return f


@overload
def ensure_async(func: TR, /) -> TR:
    ...


@overload
def ensure_async(func: TR, /) -> TR:
    ...


def ensure_async(func: Union[A, F], /) -> A:
    """Ensures that the given function is asynchronous.
    In other terms, if the function is already async, it will stay the same.
    Else, it will be converted into an async function. (Note that it will still be ran synchronously.)
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        maybe_coro = func(*args, **kwargs)

        if inspect.isawaitable(maybe_coro):
            return await maybe_coro

        return maybe_coro

    return wrapper


async def _call_later(seconds: int, func: Union[A, F]) -> None:
    await asyncio.sleep(seconds)
    await ensure_async(func)()


def call_later(seconds: int, func: Union[A, F]) -> asyncio.Task:
    return asyncio.create_task(_call_later(seconds, func))
