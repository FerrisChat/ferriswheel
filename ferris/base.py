from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    overload,
    Literal,
    TypeVar,
    TYPE_CHECKING,
    Optional,
)

from .utils import get_snowflake_creation_date


E = TypeVar('E', bound='BaseObject')

__all__ = ('SnowflakeObject', 'BaseObject', 'Object')

if TYPE_CHECKING:
    from .types import Data, Snowflake


class SnowflakeObject(ABC):
    """An abstract base class representing objects that have a snowflake ID."""

    __slots__ = ('_id',)

    def __init__(self, /) -> None:
        self._id: Optional[int] = None

    def _store_snowflake(self, id: Optional[Snowflake], /) -> None:
        self._id = id

    @property
    def id(self, /) -> Optional[int]:
        """int: The snowflake ID of this object."""
        try:
            return self._id  # type: ignore
        except AttributeError:
            return None


class BaseObject(SnowflakeObject, ABC):
    """The base class that all FerrisChat-related objects will inherit from."""

    __slots__ = ()

    @property
    def created_at(self, /) -> datetime:
        """:class:`datetime.datetime`: The creation timestamp of this object."""
        return get_snowflake_creation_date(self.id)

    @abstractmethod
    def _process_data(self, data: Any, /) -> None:
        raise NotImplementedError

    def __hash__(self, /) -> int:
        return hash(self.id)

    @overload
    def __eq__(self: E, other: E, /) -> bool:  # type: ignore
        ...

    @overload
    def __eq__(self, other: Any, /) -> Literal[False]:
        ...

    def __eq__(self, other: Any, /) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __ne__(self, other: Any, /) -> bool:
        return not self.__eq__(other)


class Object(SnowflakeObject):
    """Represents an anonymous FerrisChat-related object that has a snowflake ID.
    Instances of this may be constructed by yourself, safely.

    Parameters
    ----------
    id: int
        The snowflake ID of this object.
    """

    __slots__ = ()

    def __init__(self, id: int, /) -> None:
        super().__init__()
        self._store_snowflake(id)
