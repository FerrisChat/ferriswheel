from typing import Any, Dict, List, Protocol, Union

__all__ = ('SupportsStr', 'Snowflake', 'Data')


class SupportsStr(Protocol):
    def __str__(self) -> str:
        ...


Snowflake = int
Data = Dict[str, Union[Dict[str, Any], List[Any], Snowflake]]
