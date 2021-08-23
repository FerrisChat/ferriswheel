from typing import Any, Dict, List, Protocol, Union, runtime_checkable

__all__ = ('SupportsStr', 'SupportsId', 'Id', 'Snowflake', 'Data')


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...


Snowflake = int


@runtime_checkable
class SupportsId(Protocol):
    __slots__ = ()

    id: Snowflake


Id = Union[SupportsId, Snowflake]
Data = Dict[str, Union[Dict[str, Any], List[Any], Snowflake]]
