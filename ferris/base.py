from .types import Snowflake, DATA


class SnowflakeObject:
    """
    A base class for all classes have id attribute
    """

    def _store_snowflake(self, id: Snowflake) -> None:
        self.id = id
    
    def _process_data(self, data: DATA) -> None:
        raise NotImplementedError