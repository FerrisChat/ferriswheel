from enum import Enum


__all__ = ('ModelType', 'Pronouns')


class ModelType(Enum):
    Guild = 0
    User = 1
    Channel = 2
    Member = 3
    Role = 4


class Pronouns(Enum):
    HeHim = 0
    HeIt = 1
    HeShe = 2
    HeThey = 3
    ItHim = 4
    ItIts = 5
    ItShe = 6
    ItThey = 7
    SheHe = 8
    SheHer = 9
    SheIt = 10
    SheThey = 11
    TheyHe = 12
    TheyIt = 13
    TheyShe = 14
    TheyThem = 15
    Any = 16
    OtherAsk = 17
    Avoid = 18
