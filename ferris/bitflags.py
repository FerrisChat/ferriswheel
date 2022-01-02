from typing import Any, Callable, Type, Optional, TypeVar, Iterator, Tuple

BF = TypeVar('BF', bound='BitFlags')

__all__ = ('GuildFlags', 'UserFlags')

# Shamelessly robbed from discord.py


class Flag:
    def __init__(self, func: Callable[[Any], int]):
        self.flag = func(None)
        self.__doc__ = func.__doc__

    def __get__(self, instance: Optional[BF], owner: Type[BF]) -> Any:
        if instance is None:
            return self
        return instance._has(self.flag)

    def __set__(self, instance: BF, value: bool) -> None:
        instance._set(self.flag, value)

    def __repr__(self):
        return f'<Flag flag={self.flag!r}>'


class BitFlags:
    def __init__(self, value: int = 0) -> None:
        self._value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._value == other._value

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} value={self._value}>'

    def __iter__(self) -> Iterator[Tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, Flag):
                yield (name, self._has_flag(value.flag))

    def _has(self, o: int) -> bool:
        return (self._value & o) == o

    def _set(self, o: int, toggle: bool) -> None:
        if toggle is True:
            self._value |= o
        elif toggle is False:
            self._value &= ~o
        else:
            raise TypeError(
                f'Value to set for {self.__class__.__name__} must be a bool.'
            )


class GuildFlags(BitFlags):
    """
    Represents the flags of a :class:`~.Guild`.
    """

    __slots__ = ()

    @Flag
    def verified_guild(self):
        """:class:`bool`: Returns ``True`` if this guild's purpose has been verified (i.e. for content creators, companies, etc.)"""
        return 1 << 0

    @Flag
    def verified_scam(self):
        """:class:`bool`: Returns ``True`` if this guild has been reported and confirmed as promoting scams/other potentially harmful content"""
        return 1 << 1


class UserFlags(BitFlags):
    """
    Represents the flags of a :class:`~.User`.
    """

    __slots__ = ()

    @Flag
    def bot_account(self):
        """:class:`bool`: Returns ``True`` if this user is a bot"""
        return 1 << 0

    @Flag
    def verified_scam(self):
        """:class:`bool`: Returns ``True`` if this account is a verified scam. Verified is both verified by staff, and reported by a large amount of people."""
        return 1 << 1

    @Flag
    def possible_scam(self):
        """:class:`bool`: Returns ``True`` if this account could possibly be a scam, as many users have reported it as such."""
        return 1 << 2

    @Flag
    def compromised(self):
        """:class:`bool`: Returns ``True`` if this account has had either its email address or token changed within the past 24 hours."""
        return 1 << 3

    @Flag
    def system(self):
        """:class:`bool`: Returns ``True`` if this account is a system account."""
        return 1 << 4

    @Flag
    def early_bot(self):
        """:class:`bool`: Returns ``True`` if this bot was one of the first 100 bots created on the platform. (aka bobo bot)"""
        return 1 << 5

    @Flag
    def early_bot_dev(self):
        """:class:`bool`: Returns ``True`` if this account is the owner of one of the first 100 bots created on the platform. (aka me Cryptex)"""
        return 1 << 6

    @Flag
    def early_supporter(self):
        """:class:`bool`: Returns ``True`` if this account was one of the first 1,000 created on the platform. (aka me Cryptex but not pumpkin !!!)"""
        return 1 << 7

    @Flag
    def donator(self):
        """:class:`bool`: Returns ``True`` if this account is owned by someone who has donated to help keep the platform running, and support development."""
        return 1 << 8

    @Flag
    def library_dev(self):
        """:class:`bool` Returns ``True`` if this account is owned by a maintainer of a API wrapper for the FerrisChat API in a language (aka me Cryptex who made all of those)."""
        return 1 << 9

    @Flag
    def contributor(self):
        """:class:`bool`: Returns ``True`` if this account is owned by someone who has contributed to FerrisChat's codebase in some way. (aka me Cryptex)"""
        return 1 << 10

    @Flag
    def maintainer(self):
        """ :class:`bool`: Returns ``True`` if this account is owned by a core developer/maintainer of FerrisChat itself."""
        return 1 << 11
    
    @Flag
    def christmas_event_winner(self):
        """:class:`bool`: Returns ``True`` if this account is owned by someone who has won an official FerrisChat event."""
        return 1 << 12
    
    @Flag
    def bug_hunter(self):
        """:class:`bool`: Returns ``True`` if this account is owned by someone who has reported/discovered many important bugs in FerrisChat."""
        return 1 << 13
