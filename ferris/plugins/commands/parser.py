# Improved version of https://github.com/wumpus-py/argument-parsing/blob/master/argument_parser/core.py

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from enum import Enum
from itertools import chain
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, Generic,
                    Iterable, List, Literal, Optional, Tuple, Type, TypeVar,
                    Union, overload)

from ...utils import ensure_async
from .errors import *

ConverterOutputT = TypeVar('ConverterOutputT')
GreedyT = TypeVar('GreedyT')
LiteralT = TypeVar('LiteralT')
NotT = TypeVar('NotT')

if TYPE_CHECKING:
    from .models import Context

    ArgumentPrepareT = Callable[[str], str]
    ConverterT = Union['Converter', Type['Converter'], Callable[[str], ConverterOutputT]]
    ParserCallback = Callable[[Context, Any, ...], Any]

    ArgumentT = TypeVar('ArgumentT', bound='Argument')
    BlacklistT = TypeVar('BlacklistT', bound=ConverterT)
    ParserT = TypeVar('ParserT', bound=Union['_Subparser', 'Parser'])

_NoneType: Type[None] = type(None)

__all__ = (
    'Parser',
    'StringReader',
    'Greedy',
    'Not',
    'ConsumeType',
    'Quotes',
    'Argument',
    'Converter',
    'converter',
)


class _NullType:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return 'NULL'

    __str__ = __repr__


_NULL = _NullType()


class ConsumeType(Enum):
    """|enum|

    An enumeration of argument consumption types.

    Attributes
    ----------
    default
        The default and "normal" consumption type.
    consume_rest
        Consumes the string, including quotes, until the end.
    list
        Consumes in a similar fashion to the default consumption type,
        but will consume like this all the way until the end.
        If an error occurs, an error will be raised.
    tuple
        :attr:`~.ConsumeType.list` except that the result is a tuple,
        rather than a list.
    greedy
        Like :attr:`~.ConsumeType.list`, but it stops consuming
        when an argument fails to convert, rather than raising an error.
    """

    default      = 'default'
    consume_rest = 'consume_rest'
    list         = 'list'
    tuple        = 'tuple'
    greedy       = 'greedy'


class Quotes:
    """Builtin quote mappings. All attributes are instances of ``Dict[str, str]``.

    Attributes
    ----------
    default
        The default quote mapping.

        ``"`` -> ``"``
        ``'`` -> ``'``
    extended
        An extended quote mapping that supports
        quotes from other languages/locales.

        ``'"'``      -> ``'"'``
        ``'``        -> ``'``
        ``'\u2018'`` -> ``'\u2019'``
        ``'\u201a'`` -> ``'\u201b'``
        ``'\u201c'`` -> ``'\u201d'``
        ``'\u201e'`` -> ``'\u201f'``
        ``'\u2e42'`` -> ``'\u2e42'``
        ``'\u300c'`` -> ``'\u300d'``
        ``'\u300e'`` -> ``'\u300f'``
        ``'\u301d'`` -> ``'\u301e'``
        ``'\ufe41'`` -> ``'\ufe42'``
        ``'\ufe43'`` -> ``'\ufe44'``
        ``'\uff02'`` -> ``'\uff02'``
        ``'\uff62'`` -> ``'\uff63'``
        ``'\xab'``   -> ``'\xbb'``
        ``'\u2039'`` -> ``'\u203a'``
        ``'\u300a'`` -> ``'\u300b'``
        ``'\u3008'`` -> ``'\u3009'``
    """

    default = {
        '"': '"',
        "'": "'"
    }

    extended = {
        '"': '"',
        "'": "'",
        "\u2018": "\u2019",
        "\u201a": "\u201b",
        "\u201c": "\u201d",
        "\u201e": "\u201f",
        "\u2e42": "\u2e42",
        "\u300c": "\u300d",
        "\u300e": "\u300f",
        "\u301d": "\u301e",
        "\ufe41": "\ufe42",
        "\ufe43": "\ufe44",
        "\uff02": "\uff02",
        "\uff62": "\uff63",
        "\u2039": "\u203a",
        "\u300a": "\u300b",
        "\u3008": "\u3009",
        "\xab": "\xbb",
    }


class Greedy(Generic[GreedyT]):
    """Represents a generic type annotation that sets the
    consume-type of the argument to :attr:`~.ConsumeType.greedy`.

    Examples
    --------
    .. code:: python3

        @command()
        async def massban(ctx, members: Greedy[Member], *, reason=None):
            \"""Bans multiple people at once.\"""
            for member in members:
                await member.ban(reason=reason)
    """


class Not(Generic[NotT]):
    """A special generic type annotation that fails conversion
    if the given converter converts successfully.

    Examples
    --------
    .. code:: python3

        @command()
        async def purchase(ctx, item: Not[int], quantity: int):
            \"""Purchases an item.\"""

        @purchase.overload
        async def purchase(ctx, quantity: int, *, item: str):
            return await purchase.callback(ctx, item, quantity)
    """


class Converter(Generic[ConverterOutputT], ABC):
    """A class that aids in making class-based converters."""

    __is_converter__: bool = True

    @abstractmethod
    async def convert(self, ctx: Context, argument: str) -> ConverterOutputT:
        """|coro|

        The core conversion of the argument.
        This must be implemented, or :exc:`NotImplementedError` will be raised.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The command context being parsed.
            Note that some attributes could be ``None``.
        argument: str
            The argument to convert.

        Returns
        -------
        Any
        """
        raise NotImplementedError

    # noinspection PyUnusedLocal
    async def validate(self, ctx: Context, argument: str) -> bool:
        """|coro|

        The argument validation check to use.
        This will be called before convert and raise a :exc:`~.ValidationError`
        if it fails.

        This exists to encourage cleaner code.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The command context being parsed.
            Note that some attributes could be ``None``.
        argument: str
            The argument to validate.

        Returns
        -------
        bool
        """
        return True


class LiteralConverter(Converter[LiteralT]):
    def __init__(self, *choices: LiteralT) -> None:
        self._valid: Tuple[LiteralT, ...] = choices

    def __repr__(self) -> None:
        return f'<{self.__class__.__name__} valid={self._valid!r}>'

    async def convert(self, ctx: Context, argument: str) -> LiteralT:
        for possible in self._valid:
            p_type = type(possible)
            try:
                casted = await _convert_one(ctx, argument, p_type)
            except ConversionError:
                continue
            else:
                if casted not in self._valid:
                    raise BadLiteralArgument(argument, self._valid)

                return casted

        raise BadLiteralArgument(argument, self._valid)


class _Not(Converter[str]):
    def __init__(self, *entities: BlacklistT) -> None:
        self._blacklist: Tuple[BlacklistT, ...] = entities

    def __repr__(self) -> None:
        return f'<{self.__class__.__name__} blacklist={self._blacklist!r}>'

    async def convert(self, ctx: Context, argument: str) -> str:
        for entity in self._blacklist:
            try:
                await _convert_one(ctx, argument, entity)
            except ConversionError:
                return argument
            else:
                raise BlacklistedArgument(argument, entity)


_SC = 'Tuple[Tuple[ConverterT], Optional[bool], Optional[ConsumeType]]'


def _sanitize_converter(converter: ConverterT, /, optional: bool = None, consume: ConsumeType = None) -> _SC:
    origin = getattr(converter, '__origin__', False)
    args = getattr(converter, '__args__', False)

    if origin and args:
        if origin is Union:
            if _NoneType in args or None in args:
                # This is an optional type.
                optional = True
                args = tuple(arg for arg in args if arg is not _NoneType)

            return tuple(
                chain.from_iterable(_sanitize_converter(arg)[0] for arg in args)
            ), optional, consume

        if origin is Literal:
            converter = LiteralConverter(*args)

        if origin is List:
            consume = ConsumeType.list
            return _sanitize_converter(args[0], optional, consume)

        if origin is Greedy:
            consume = ConsumeType.greedy

        if origin is Not:
            converter = _Not(*args)

    if inspect.isclass(converter) and issubclass(converter, Converter):
        converter = converter()

    return (converter,), optional, consume


def _convert_bool(argument: str) -> bool:
    if isinstance(argument, bool):
        return argument

    argument = argument.lower()
    if argument in {'true', 't', 'yes', 'y', 'on', 'enable', 'enabled', '1'}:
        return True
    if argument in {'false', 'f', 'no', 'n', 'off', 'disable', 'disabled', '0'}:
        return False

    raise BadBooleanArgument(argument)


async def _convert_one(ctx: Context, argument: str, converter: ConverterT) -> ConverterOutputT:
    if converter is bool:
        return _convert_bool(converter)

    try:
        if getattr(converter, '__is_converter__', False):
            return await converter.convert(ctx, argument)

        return converter(argument)

    except Exception as exc:
        raise ConversionError(exc)


async def _convert(ctx: Context, argument: Argument, word: str, converters: Iterable[ConverterT]) -> ConverterOutputT:
    errors = []
    for converter in converters:
        try:
            result = await _convert_one(ctx, word, converter)

            if getattr(converter, '__is_converter__', False) and not await converter.validate(ctx, result):
                raise ArgumentValidationError(ctx, argument, word)

            return result

        except ConversionError as exc:
            errors.append(exc)

    raise ConversionFailure(ctx, argument, word, *errors)


def _prepare(ctx: Context, argument: Argument, word: str) -> str:
    callback = argument.prepare

    if callback is None:
        return word

    try:
        return str(callback(word))
    except Exception as exc:
        raise ArgumentPreparationError(ctx, argument, word, exc)


class Argument:
    """Represents a positional argument.

    Although these are automatically constructed, you can
    explicitly construct these and use them as type-annotations
    in your command signatures.

    Parameters
    ----------
    converter
        The converter for this argument. This cannot be mixed with `converters`.
    *converters
        A list of converters for this argument. This cannot be mixed with `converter`.
    name: str
        The name of this argument.
    signature: str
        A custom signature for this argument. Will be auto-generated if not given.
    default
        The default value of this argument.
    optional: bool
        Whether or not this argument is optional.
    description: str
        A description about this argument.
    consume_type: :class:`~.ConsumeType`
        The consumption type of this argument.
    quoted: bool
        Whether or not this argument can be pass in with quotes.
    quotes: Dict[str, str]
        A mapping of start-quotes to end-quotes
        of all supported quotes for this argument.
    **kwargs
        Extra kwargs to pass in for metadata.

    Attributes
    ----------
    name: str
        The name of this argument.
    default
        The default value of this argument.
    optional: bool
        Whether or not this argument is optional.
    description: str
        A description about this argument.
    consume_type: :class:`~.ConsumeType`
        The consumption type of this argument.
    quoted: bool
        Whether or not this argument can be pass in with quotes.
    quotes: Dict[str, str]
        A mapping of start-quotes to end-quotes
        of all supported quotes for this argument.
    prepare: Callable[[str], str]
        A callable that takes a string, which will
        prepare the argument before conversion.

    Examples
    --------
    .. code:: python3

        @command()
        async def translate(
            ctx,
            language: Argument(
                Literal['spanish', 'french', 'chinese'],
                prepare=str.lower
            ),
            text: Argument(str, consume_type=ConsumeType.consume_rest)
        ):
            ...
    """

    if TYPE_CHECKING:
        @overload
        def __init__(
            self,
            /,
            converter: ConverterT,
            *,
            name: str = None,
            signature: str = None,
            default: Any = _NULL,
            optional: bool = None,
            description: str = None,
            consume_type: Union[ConsumeType, str] = ConsumeType.default,
            quoted: bool = None,
            quotes: Dict[str, str] = None,
            prepare: ArgumentPrepareT = None,
            **kwargs
        ) -> None:
            ...

        @overload
        def __init__(
            self,
            /,
            *converters: ConverterT,
            name: str = None,
            alias: str = None,
            signature: str = None,
            default: Any = _NULL,
            optional: bool = None,
            description: str = None,
            consume_type: Union[ConsumeType, str] = ConsumeType.default,
            quoted: bool = None,
            quotes: Dict[str, str] = None,
            prepare: ArgumentPrepareT = None,
            **kwargs
        ) -> None:
            ...

    def __init__(
        self,
        /,
        *converters: ConverterT,
        name: str = None,
        signature: str = None,
        default: Any = _NULL,
        optional: bool = None,
        description: str = None,
        converter: ConverterT = None,
        consume_type: Union[ConsumeType, str] = ConsumeType.default,
        quoted: bool = None,
        quotes: Dict[str, str] = None,
        prepare: ArgumentPrepareT = None,
        **kwargs
    ) -> None:
        actual_converters = str,

        if converters and converter is not None:
            raise ValueError('Converter kwarg cannot be used when they are already passed as positional arguments.')

        if len(converters) == 1:
            converter = converters[0]
            converters = ()

        if converters or converter:
            if converters:
                actual_converters, optional_, consume = _sanitize_converter(converters[0])
                actual_converters += _sanitize_converter(converters[1:])[0]
            elif converter:
                actual_converters, optional_, consume = _sanitize_converter(converter)
            else:
                raise ValueError('Parameter mismatch')

            optional = optional if optional is not None else optional_
            consume_type = consume_type if consume_type is not None else consume

        self._param_key: Optional[str] = None
        self._param_kwarg_only: bool = False
        self._param_var_positional: bool = False

        self.name: str = name
        self.description: str = description
        self.default: Any = default
        self.prepare: ArgumentPrepareT = prepare

        self.consume_type: ConsumeType = (
            consume_type if isinstance(consume_type, ConsumeType) else ConsumeType(consume_type)
        )

        self.optional: bool = optional if optional is not None else False
        self.quoted: bool = quoted if quoted is not None else consume_type is not ConsumeType.consume_rest
        self.quotes: Dict[str, str] = quotes if quotes is not None else Quotes.default

        self._signature: str = signature
        self._converters: Tuple[ConverterT, ...] = actual_converters

        self._kwargs: Dict[str, Any] = kwargs

    def __repr__(self) -> str:
        return f'<Argument name={self.name!r} optional={self.optional} consume_type={self.consume_type}>'

    def __hash__(self) -> int:
        return hash(id(self))

    @property
    def converters(self) -> List[ConverterT]:
        """List[Union[type, :class:`~.Converter`]]: A list of this argument's converters."""
        return list(self._converters)

    @property
    def signature(self) -> str:
        """str: The signature of this argument."""
        if self._signature is not None:
            return self._signature

        start, end = '[]' if self.optional or self.default is not _NULL else '<>'

        suffix = '...' if self.consume_type in (
            ConsumeType.list, ConsumeType.tuple, ConsumeType.greedy
        ) else ''

        default = f'={self.default}' if self.default is not _NULL else ''
        return start + str(self.name) + default + suffix + end

    @signature.setter
    def signature(self, value: str, /) -> str:
        self._signature = value

    @classmethod
    def _from_parameter(cls: Type[ArgumentT], param: inspect.Parameter, /) -> ArgumentT:
        def finalize(argument: ArgumentT) -> ArgumentT:
            if param.kind is param.KEYWORD_ONLY:
                argument._param_kwarg_only = True

            if param.kind is param.VAR_POSITIONAL:
                argument._param_var_positional = True

            argument._param_key = store = param.name
            if not argument.name:
                argument.name = store

            return argument

        kwargs = {'name': param.name}

        if param.annotation is not param.empty:
            if isinstance(param.annotation, cls):
                return finalize(param.annotation)

            kwargs['converter'] = param.annotation

        if param.default is not param.empty:
            kwargs['default'] = param.default

        if param.kind is param.KEYWORD_ONLY:
            kwargs['consume_type'] = ConsumeType.consume_rest

        elif param.kind is param.VAR_POSITIONAL:
            kwargs['consume_type'] = ConsumeType.tuple

        return finalize(cls(**kwargs))


class StringReader:
    """Helper class to aid with parsing strings.

    Parameters
    ----------
    string: str
        The string to parse.
    quotes: Dict[str, str]
        A mapping of start-quotes to end-quotes.
        Defaults to :attr:`~.Quotes.default`
    """

    class EOF:
        """The pointer has gone past the end of the string."""

    def __init__(self, string: str, /, *, quotes: Dict[str, str] = None) -> None:
        self.quotes: Dict[str, str] = quotes or Quotes.default
        self.buffer: str = string
        self.index: int = -1

    def seek(self, index: int, /) -> str:
        """Seek to an index in the string.

        Parameters
        ----------
        index: int
            The index to seek to.

        Returns
        -------
        str
        """
        self.index = index
        return self.current

    @property
    def current(self) -> Union[str, Type[EOF]]:
        """str: The current character this reader is pointing to."""
        try:
            return self.buffer[self.index]
        except IndexError:
            return self.EOF

    @property
    def eof(self) -> bool:
        """bool: Whether or not this reader has reached the end of the string."""
        return self.current is self.EOF

    def previous_character(self) -> str:
        """Seeks to the previous character in the string."""
        return self.seek(self.index - 1)

    def next_character(self) -> str:
        """Seeks to the next character in the string."""
        return self.seek(self.index + 1)

    @property
    def rest(self) -> str:
        """str: The rest of the characters in the string."""
        result = self.buffer[self.index:] if self.index != -1 else self.buffer
        self.index = len(self.buffer)  # Force an EOF
        return result

    @staticmethod
    def _is_whitespace(char: str, /) -> bool:
        if char is ...:
            return False
        return char.isspace()

    def skip_to_word(self) -> None:
        """Skips to the beginning of the next word."""
        char = ...
        while self._is_whitespace(char):
            char = self.next_character()

    def next_word(self, *, skip_first: bool = True) -> str:
        """Returns the next word in the string.

        Parameters
        ----------
        skip_first: bool
            Whether or not to call :meth:`~.StringReader.skip_to_word`
            beforehand. Defaults to ``True``.

        Returns
        -------
        str
        """
        char = ...
        buffer = ''

        if skip_first:
            self.skip_to_word()

        while not self._is_whitespace(char):
            char = self.next_character()
            if self.eof:
                return buffer

            buffer += char

        buffer = buffer[:-1]
        return buffer

    def next_quoted_word(self, *, skip_first: bool = True) -> str:
        """Returns the next quoted word in the string.

        Parameters
        ----------
        skip_first: bool
            Whether or not to call :meth:`~.StringReader.skip_to_word`
            beforehand. Defaults to ``True``.

        Returns
        -------
        str
        """
        if skip_first:
            self.skip_to_word()

        first_char = self.next_character()

        if first_char not in self.quotes:
            self.previous_character()
            return self.next_word(skip_first=False)

        end_quote = self.quotes[first_char]

        char = ...
        buffer = ''

        while char != end_quote or self.buffer[self.index - 1] == '\\':
            char = self.next_character()
            if self.eof:
                return buffer

            buffer += char

        self.next_character()
        buffer = buffer[:-1]
        return buffer


class _Subparser:
    """Parses one specific overload."""

    def __init__(self, arguments: List[Argument] = None, *, callback: ParserCallback = None):
        self._arguments: List[Argument] = arguments or []
        self.callback: Optional[ParserCallback] = callback

    def __hash__(self) -> int:
        return hash(id(self))

    def add_argument(self, argument: Argument, /) -> None:
        self._arguments.append(argument)

    @property
    def signature(self) -> str:
        """str: The signature (or "usage string") for this overload."""
        return ' '.join(arg.signature for arg in self._arguments)

    @classmethod
    def from_function(cls: Type[P], func: ParserCallback, /) -> P:
        """Creates a new :class:`~.Parser` from a function."""
        params = list(inspect.signature(func).parameters.values())

        if len(params) < 1:
            raise TypeError('Command callback must have at least one context parameter.')

        self = cls(callback=func)
        for param in params[1:]:
            self.add_argument(Argument._from_parameter(param))

        return self

    async def parse(self, text: str, /, ctx: Context) -> Tuple[List[Any], Dict[str, Any]]:
        # Return a tuple (args: list, kwargs: dict)
        # Execute as callback(ctx, *args, **kwargs)

        args = ctx.args = []
        kwargs = ctx.kwargs = {}
        reader = ctx.reader = StringReader(text)

        def append_value(argument: Argument, value: Any) -> None:
            if argument._param_kwarg_only:
                kwargs[argument._param_key] = value
            elif argument._param_var_positional:
                args.extend(value)
            else:
                args.append(value)

        i = 0
        for i, argument in enumerate(self._arguments, start=1):
            if reader.eof:
                i -= 1
                break

            start = reader.index

            if argument.consume_type not in (ConsumeType.consume_rest, ConsumeType.default):
                # Either list, tuple, or greedy
                result = []

                while not reader.eof:
                    word = reader.next_quoted_word() if argument.quoted else reader.next_word()
                    word = _prepare(ctx, argument, word)
                    try:
                        word = await _convert(ctx, argument, word, argument.converters)
                    except ConversionError as exc:
                        if argument.consume_type is not ConsumeType.greedy:
                            raise exc
                        break
                    else:
                        result.append(word)

                if argument.consume_type is ConsumeType.tuple:
                    result = tuple(result)

                append_value(argument, result)
                continue

            if argument.consume_type is ConsumeType.consume_rest:
                word = reader.rest.strip()
            else:
                word = reader.next_quoted_word() if argument.quoted else reader.next_word()

            word = _prepare(ctx, argument, word)

            try:
                word = await _convert(ctx, argument, word, argument.converters)
            except ConversionError as exc:
                if argument.optional:
                    default = argument.default if argument.default is not _NULL else None
                    append_value(argument, default)
                    reader.seek(start)
                    continue

                raise exc
            else:
                append_value(argument, word)

        for argument in self._arguments[i:]:
            if argument.default is not _NULL:
                append_value(argument, argument.default)
            elif argument.optional:
                append_value(argument, None)
            else:
                raise MissingArgumentError(ctx, argument)

        return args, kwargs


class Parser:
    """The main class that parses arguments."""

    def __init__(self, *, overloads: List[_Subparser] = None) -> None:
        self._overloads: List[_Subparser] = overloads or []

    @property
    def _main_parser(self) -> _Subparser:
        if not len(self._overloads):
            self._overloads.append(_Subparser())

        return self._overloads[0]

    @property
    def callback(self) -> ParserCallback:
        """Callable[[:class:`~.Context`, Any, ...], Any]: The callback of this command."""
        return self._main_parser.callback

    @callback.setter
    def callback(self, func: ParserCallback) -> None:
        func = ensure_async(func)
        overload = _Subparser.from_function(func)
        try:
            self._overloads[0] = overload
        except IndexError:
            self._overloads = [overload]

    @property
    def signature(self) -> str:
        """str: The usage string of this command."""
        return self._main_parser.signature

    @property
    def arguments(self) -> List[Argument]:
        """List[:class:`~.Argument`]: A list of arguments this command takes."""
        return self._main_parser._arguments

    def overload(self: ParserT, func: ParserCallback, /) -> ParserT:
        """Adds a command overload to this function."""
        func = ensure_async(func)
        result = _Subparser.from_function(func)
        self._overloads.append(result)
        return self

    @classmethod
    def from_function(cls: Type[ParserT], func: ParserCallback, /) -> ParserT:
        func = ensure_async(func)
        parser = _Subparser.from_function(func)
        return cls(overloads=[parser])

    async def _parse(self, text: str, /, ctx: Context) -> Tuple[ParserCallback, List[Any], Dict[str, Any]]:
        errors = []
        for overload in self._overloads:
            try:
                return overload.callback, *await overload.parse(text, ctx=ctx)
            except Exception as exc:
                errors.append(exc)

        # Maybe do something with the other errors?
        raise errors[0]


def converter(func: Callable[[Context, str], Awaitable[ConverterOutputT]]) -> Type[Converter[ConverterOutputT]]:
    """A decorator that helps convert a function into a converter.

    Examples
    --------
    .. code:: python3

        @converter
        async def reverse_string(ctx, argument):
            return argument[::-1]

        @command('reverse')
        async def reverse_command(ctx, *, text: reverse_string):
            \"""Reverses a string of text.\"""
            await ctx.send(text)
    """
    func = ensure_async(func)

    async def convert(_, ctx: Context, argument: str) -> ConverterOutputT:
        return await func(ctx, argument)

    return type('FunctionBasedConverter', (Converter,), {'convert': convert})
