from typing import Protocol, Type, Union, runtime_checkable, Optional
from typing_extensions import TypeAlias

__all__ = ('SupportsStr', 'SupportsId', 'Id', 'Snowflake')


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...


Snowflake: TypeAlias = int


@runtime_checkable
class SupportsId(Protocol):
    __slots__ = ()

    id: Snowflake


Id: TypeAlias = Optional[Union[SupportsId, Snowflake]]
