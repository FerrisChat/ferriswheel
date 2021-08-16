from enum import Enum


__all__ = ('ModelType',)


class ModelType(Enum):
    Guild = 0
    User = 1
    Channel = 2
    Member = 3
