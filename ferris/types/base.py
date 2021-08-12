from typing import Dict, Union, List, Any

__all__ = ('Snowflake', 'DATA', )

Snowflake = int
Data = Dict[str, Union[Dict[str, Any], List[Any], Snowflake]]
