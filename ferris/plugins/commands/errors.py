from __future__ import annotations

from typing import Any, Optional, Tuple, TYPE_CHECKING
from ...utils import to_error_string
from ferris.errors import FerrisException

if TYPE_CHECKING:
    from .models import Context
    from .parser import Argument

__all__ = (
    'CommandBasedError',
    'ArgumentParsingError',
    'ArgumentPreparationError',
    'ArgumentValidationError',
    'ConversionError',
    'ConversionFailure',
    'MissingArgumentError',
    'BadBooleanArgument',
    'BadLiteralArgument',
    'BlacklistedArgument',
    'BadArgument',
    'CommandNotFound',
)


class CommandBasedError(FerrisException):
    """The base exception raised for errors related to the commands plugin."""


class ArgumentParsingError(CommandBasedError):
    """Raised when an error occurs during argument parsing."""


class ArgumentValidationError(ArgumentParsingError):
    """Raised when an argument fails validation.

    Attributes
    ----------
    ctx: :class:`~.Context`
        The context that raised this error.
    argument: :class:`~.Argument`
        The argument that failed validation.
    word: str
        The literal string that did not make it past validation.
    """

    def __init__(self, ctx: Context, argument: Argument, word: str) -> None:
        self.ctx: Context = ctx
        self.argument: Argument = argument
        self.word: str = word
        super().__init__(f'Argument {argument.name!r} did not pass validation.')


class ArgumentPreparationError(ArgumentParsingError):
    """Raised when an argument fails preparation.

    In other words, this exception is raised when an error
    occurs during :attr:`~.Argument.prepare`.

    Attributes
    ----------
    ctx: :class:`~.Context`
        The context that raised this error.
    argument: :class:`~.Argument`
        The argument that failed preparation.
    word: str
        The string of the word that could not be prepared.
    error: :exc:`Exception`
        The error that was raised.
    """

    def __init__(self, ctx: Context, argument: Argument, word: str, exc: Exception) -> None:
        self.ctx: Context = ctx
        self.argument: Argument = argument
        self.word: str = word
        self.error: Exception = exc

        super().__init__(f'Argument {argument.name!r} failed preparation: {to_error_string(exc)}')


class MissingArgumentError(ArgumentParsingError):
    """Raised when an argument is missing.

    Attributes
    ----------
    ctx: :class:`~.Context`
        The context that raised this error.
    argument: :class:`~.Argument`
        The argument that was missing.
    """

    def __init__(self, ctx: Context, argument: Argument) -> None:
        self.ctx: Context = ctx
        self.argument: Argument = argument
        super().__init__(f'Missing required argument {argument.name!r}.')


class ConversionError(ArgumentParsingError):
    """Raised when an error occurs during argument conversion."""


class ConversionFailure(ConversionError):
    """Raised when an unhandled error occurs during argument conversion.

    Attributes
    ----------
    ctx: :class:`~.Context`
        The context that raised this error.
    argument: :class:`~.Argument`
        The argument that failed conversion.
    word: str
        The literal argument string that failed conversion.
    errors: Tuple[:exc:`Exception`, ...]
        The errors that were raised.
    """

    def __init__(self, ctx: Context, argument: Argument, word: str, *errors: Exception) -> None:
        self.ctx: Context = ctx
        self.argument: Argument = argument
        self.word: str = word

        self.errors: Tuple[Exception, ...] = errors
        super().__init__(f'Argument {argument.name!r} failed conversion: {to_error_string(self.error)}')

    @property
    def error(self) -> Optional[Exception]:
        """The most recent error raised, or ``None``."""
        try:
            return self.errors[-1]
        except IndexError:
            return None


class BadArgument(ConversionError):
    """A user defined error that should be raised if an argument cannot
    be converted during argument conversion."""


class BadBooleanArgument(BadArgument):
    """Raised when converting an argument to a boolean fails."""

    def __init__(self, argument: str) -> None:
        super().__init__(f'{argument!r} cannot be represented as a boolean.')


class BadLiteralArgument(BadArgument):
    """Raised when converting to a ``Literal`` generic fails."""

    def __init__(self, argument: str, choices: Tuple[Any, ...]) -> None:
        self.argument: str = argument
        self.choices: Tuple[Any, ...] = choices
        super().__init__(f'{argument!r} is not a valid choice.')


class BlacklistedArgument(BadArgument):
    """Raised when converting to a ``Not`` generic is successful."""

    def __init__(self, argument: str, blacklist: type) -> None:
        self.argument: str = argument
        self.blacklist: type = blacklist
        super().__init__(f'{argument!r} should not be castable into {blacklist!r}.')


class CommandNotFound(CommandBasedError):
    """Raised when a command is not found.

    Attributes
    ----------
    ctx: :class:`~.Context`
        The context that raised this error.
    invoked_with: str
        The string that did not correspond to a command.
    """

    def __init__(self, ctx: Context) -> None:
        self.ctx: Context = ctx
        self.invoked_with: str = ctx.invoked_with
        super().__init__(f'Command {self.invoked_with!r} is not found.')
