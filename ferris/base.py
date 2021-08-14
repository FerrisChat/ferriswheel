from abc import ABC, abstractmethod
from datetime import datetime

from .types import Snowflake, Data
from .utils import get_snowflake_creation_date


class SnowflakeObject(ABC):
    """An abstract base class representing objects that have a snowflake ID."""

    def __init__(self) -> None:
        self.__id: int = None

    def _store_snowflake(self, id: Snowflake, /) -> None:
        self.__id = id

    @property
    def id(self) -> int:
        """int: The snowflake ID of this object."""
        return self.__id


class BaseObject(SnowflakeObject, ABC):
    """The base class that all FerrisChat-related objects will inherit from."""

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: The creation timestamp of this object."""
        return get_snowflake_creation_date(self.id)

    @abstractmethod
    def _process_data(self, data: Data) -> None:
        raise NotImplementedError


class Object(SnowflakeObject):
    """Represents an anonymous FerrisChat-related object that has a snowflake ID.
    Instances of this may be constructed by yourself, safely.

    Parameters
    ----------
    id: int
        The snowflake ID of this object.
    """

    def __init__(self, id: int) -> None:
        super().__init__()
        self._store_snowflake(id)
