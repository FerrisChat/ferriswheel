from typing import Protocol, Union, runtime_checkable, Optional

__all__ = ('SupportsStr', 'SupportsId', 'Id', 'Snowflake')


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...


Snowflake = int


@runtime_checkable
class SupportsId(Protocol):
    __slots__ = ()

    id: Snowflake


Id = Optional[Union[SupportsId, Snowflake]]
