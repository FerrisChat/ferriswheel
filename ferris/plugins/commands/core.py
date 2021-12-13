from __future__ import annotations

import functools

from typing import (
    Any,
    Awaitable,
    Callable,
    Collection,
    Dict,
    Generator,
    List,
    Optional,
    overload,
    Type,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

from .errors import CommandBasedError, CommandNotFound
from .models import Command, Context
from .parser import StringReader
from ...message import Message
from ...client import Client
from ...utils import ensure_async

V = TypeVar('V')

if TYPE_CHECKING:
    from .models import CommandCallback

    DefaultT = TypeVar('DefaultT')

    BasePrefixT = Union[str, Collection[str]]
    FunctionPrefixT = Callable[['Bot', Message], Awaitable[BasePrefixT]]
    PrefixT = Union[BasePrefixT, FunctionPrefixT]

__all__ = (
    'CaseInsensitiveDict',
    'CommandSink',
    'Bot',
)


class CaseInsensitiveDict(Dict[str, V]):
    """Represents a case-insensitive dictionary."""

    def __getitem__(self, key: str) -> V:
        return super().__getitem__(key.casefold())

    def __setitem__(self, key: str, value: V) -> None:
        super().__setitem__(key.casefold(), value)

    def __delitem__(self, key: str) -> None:
        return super().__delitem__(key.casefold())

    def __contains__(self, key: str) -> bool:
        return super().__contains__(key.casefold())

    def get(self, key: str, default: DefaultT = None) -> Union[V, DefaultT]:
        return super().get(key.casefold(), default)

    def pop(self, key: str, default: DefaultT = None) -> Union[V, DefaultT]:
        return super().pop(key.casefold(), default)

    get.__doc__ = dict.get.__doc__
    pop.__doc__ = dict.pop.__doc__


class CommandSink:
    """Represents a sink of commands.
    This will both mixin to :class:`~.Bot` and :class:`~.CommandGroup`.

    Attributes
    ----------
    command_mapping: Dict[str, :class:`.Command`]
        A full mapping of command names to commands.
    """

    if TYPE_CHECKING:
        command_mapping: Union[Dict[str, Command], CaseInsensitiveDict[Command]]

    def __init__(self, *, case_insensitive: bool = False) -> None:
        mapping_factory = CaseInsensitiveDict if case_insensitive else dict
        self.command_mapping = mapping_factory()

    def walk_commands(self) -> Generator[Command, None, None]:
        """Returns a generator that walks through all of the commands
        this sink holds.

        Returns
        -------
        Generator[:class:`.Command`, None, None]
        """
        seen = set()

        for command in self.command_mapping.values():
            if command not in seen:
                seen.add(command)
                yield command

    def get_command(self, name: str, /, default: DefaultT = None) -> Union[Command, DefaultT]:
        """Tries to get a command by it's name.
        Aliases are supported.

        Parameters
        ----------
        name: str
            The name of the command you want to lookup.
        default
            What to return instead if the command was not found.
            Defaults to ``None``.

        Returns
        -------
        Optional[:class:`~.Command`]
            The command found.
        """
        return self.command_mapping.get(name, default)

    @overload
    def command(
        self,
        name: str,
        *,
        alias: str = None,
        brief: str = None,
        description: str = None,
        usage: str = None,
        cls: Type[Command] = Command,
        **kwargs
    ) -> Callable[[CommandCallback], Command]:
        ...

    @overload
    def command(
        self,
        name: str,
        *,
        aliases: Collection[str] = None,
        brief: str = None,
        description: str = None,
        usage: str = None,
        cls: Type[Command] = Command,
        **kwargs
    ) -> Callable[[CommandCallback], Command]:
        ...

    def command(
        self,
        name: str,
        *,
        alias: str = None,
        aliases: Collection[str] = None,
        brief: str = None,
        description: str = None,
        usage: str = None,
        cls: Type[Command] = Command,
        **kwargs
    ) -> Callable[[CommandCallback], Command]:
        """Returns a decorator that adds a command to this command sink."""
        
        if alias and aliases:
            raise ValueError('Only one of alias or aliases can be set.')

        if alias:
            aliases = [alias]
        elif not aliases:
            aliases = []

        def decorator(callback: CommandCallback, /) -> Command:
            command = cls(
                callback,
                name=str(name),
                aliases=aliases,
                brief=brief, 
                description=description,
                usage=usage,
                **kwargs
            )

            self.command_mapping[name] = command
            for alias in aliases:
                self.command_mapping[alias] = command

            return command

        return decorator

    @property
    def commands(self) -> List[Command]:
        """List[:class:`.Command`]: A list of the commands this sink holds."""
        return list(self.walk_commands())

    def remove_command(self, name: str) -> Optional[Command]:
        """
        Remove a command or alias from this command sink.

        Parameters
        -----------
        name: :class:`str`
            The name of the command or alias to remove.

        Returns
        --------
        Optional[:class:`~.Command`]
            The command that was removed.
            If the name is invalid, ``None`` is returned instead.
        """
        command = self.command_mapping.pop(name)

        if command:
            if name in command.aliases:  # This is an alias, so don't remove the command, only this alias.
                return command

            for alias in command.aliases:
                self.command_mapping.pop(alias)

        return command


class Bot(Client, CommandSink):
    """Represents a bot with extra command handling support.

    Parameters
    ----------
    prefix
        The prefix this bot will listen for. This is required.
    case_insensitive: bool
        Whether or not commands should be case-insensitive.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The event loop to use for the client. If not passed, then the default event loop is used.
    max_messages_count: Optional[int]
        The maximum number of messages to store in the internal message buffer.
        Defaults to ``1000``.
    
    max_heartbeat_timeout: Optional[int]
        The maximum timeout in seconds between sending a heartbeat to the server.
        If heartbeat took longer than this timeout, the client will attempt to reconnect.
    """

    def __init__(
        self, 
        prefix: PrefixT,
        *, 
        case_insensitive: bool = False,
        prefix_case_insensitive: bool = False,
        strip_after_prefix: bool = False,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        CommandSink.__init__(self, case_insensitive=case_insensitive)

        self.prefix: PrefixT = self._sanitize_prefix(prefix, case_insensitive=prefix_case_insensitive)
        self.strip_after_prefix: bool = bool(strip_after_prefix)

        self._prefix_case_insensitive: bool = bool(prefix_case_insensitive)
        self._default_case_insensitive: bool = bool(case_insensitive)

    @staticmethod
    def _sanitize_prefix(prefix: Any, *, case_insensitive: bool = False, allow_callable: bool = True) -> PrefixT:
        if prefix is None:
            return ''

        if isinstance(prefix, str):
            if case_insensitive:
                return prefix.casefold()

            return prefix

        if isinstance(prefix, Collection):
            try:
                invalid = next(filter(lambda item: not isinstance(item, str), prefix))
            except StopIteration:
                pass
            else:
                raise TypeError(f'Prefix collection must only consist of strings, not {type(invalid)!r}.')

            res = list(map(str.casefold, prefix)) if case_insensitive else list(prefix)
            return sorted(res, key=len, reverse=True)

        if callable(prefix) and allow_callable:
            return _ensure_casefold(ensure_async(prefix), case_insensitive=case_insensitive)

        raise TypeError(
            f'Invalid prefix {prefix!r}. Only strings, collections of strings, '
            f'or functions that return them are allowed.'
        )

    async def get_prefix(self, message: Message, *, prefix: BasePrefixT = None) -> Optional[BasePrefixT]:
        """Gets the prefix, or list of prefixes from the given message.
        If the message does not start with a prefix, ``None`` is returned.

        Parameters
        ----------
        message: :class:`~.Message`
            The message to get the prefix from.

        Returns
        -------
        Union[str, List[str]]
        """
        prefix = self.prefix if prefix is None else prefix
        content = message.content

        if self._prefix_case_insensitive:
            content = content.casefold()

        if isinstance(prefix, str):
            if content.startswith(prefix):
                return prefix
            else:
                return None

        if isinstance(prefix, list):
            try:
                return next(filter(lambda pf: content.startswith(pf), prefix))
            except StopIteration:
                return None

        if callable(prefix):
            prefix = await prefix(self, message)
            return self.get_prefix(message, prefix=prefix)

        return None

    async def get_context(self, message: Message, *, cls: Type[Context] = Context) -> Context:
        """Parses a :class:`~.Context` out of a message.

        If the message is not a command,
        partial context with only the ``message`` parameter is returned.

        If an error occurs during parsing,
        attributes of the returned context may remain as ``None``.

        Parameters
        ----------
        message: :class:`~.Message`
            The message to get the context from.
        cls: Type[:class:`~.Context`]
            The context subclass to use. Defaults to :class:`~.Context`.

        Returns
        -------
        :class:`~.Context`
        """
        ctx = cls(self, message)
        prefix = await self.get_prefix(message)

        if prefix is None:
            return ctx

        ctx.prefix = prefix
        content = message.content[len(prefix):]

        if self.strip_after_prefix:
            content = content.strip()

        reader = ctx.reader = StringReader(content)
        ctx.invoked_with = word = reader.next_word(skip_first=False)
        ctx.command = self.command_mapping.get(word)
        return ctx

    async def invoke(self, ctx: Context) -> None:
        """Parses and invokes the given context.

        Checks, cooldowns, hooks, etc. are ran here.
        See :meth:`~.Context.reinvoke` for a version that bypasses these.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The context to invoke.
        """
        try:
            if not ctx.command:
                if ctx.invoked_with is not None:
                    raise CommandNotFound(ctx)
                else:
                    return

            rest = ctx.reader.rest.strip()
            await ctx.command.execute(ctx, rest)

        except CommandBasedError as exc:
            self.dispatch('command_error', exc)


def _ensure_casefold(func: FunctionPrefixT, /, *, case_insensitive: bool = False) -> FunctionPrefixT:
    @functools.wraps(func)
    async def wrapper(bot: Bot, message: Message) -> BasePrefixT:
        return bot._sanitize_prefix(
            await func(bot, message),
            case_insensitive=case_insensitive,
            allow_callable=False
        )

    return wrapper
