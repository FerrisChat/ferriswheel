from __future__ import annotations

import inspect
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Collection, Dict,
                    Generic, List, Optional, Tuple, TypeVar)

from ...message import Message
from .parser import Parser

R = TypeVar('R')

if TYPE_CHECKING:
    from ferris import Channel, Guild, Message, User
    from typing_extensions import Concatenate, ParamSpec

    from .core import Bot
    from .parser import StringReader

    P = ParamSpec('P')
    CommandCallback = Callable[Concatenate['Context', P], Awaitable[R]]
    ErrorCallback = Callable[['Context', Exception], Awaitable[Any]]
else:
    P = TypeVar('P')

__all__ = (
    'Command',
    'Context',
)


class Command(Parser, Generic[P, R]):
    """Represents a command.

    Attributes
    ----------
    name: str
        The name of this command.
    aliases: List[str]
        A list of aliases for this command.
    usage: str
        The custom usage string for this command, or ``None``.
        See :attr:`~.Command.signature` for an auto-generated version.
    error_callback: Optional[Callable[[:class:`~.Context`, Exception], Any]]
        The callback for when an error is raise during command invokation.
        This could be ``None``.
    """

    def __init__(
        self,
        callback: CommandCallback,
        *,
        name: str,
        aliases: Collection[str],
        brief: Optional[str] = None,
        description: Optional[str] = None,
        usage: Optional[str] = None,
        **attrs
    ) -> None:
        self.error_callback: Optional[ErrorCallback] = None

        self.name: str = name
        self.aliases: List[str] = list(aliases)
        self.usage: Optional[str] = usage

        self._brief: Optional[str] = brief
        self._description: Optional[str] = description

        self._metadata: Dict[str, Any] = attrs

        super().__init__()
        self.overload(callback)

    def __str__(self) -> str:
        return self.qualified_name

    def __repr__(self) -> str:
        return f'<Command name={self.name!r} brief={self.brief!r}>'

    def __hash__(self) -> int:
        return hash(self.qualified_name)

    @property
    def brief(self) -> str:
        """str: A short description of this command.
        
        If no brief is set, the first line of the :attr:`~.Command.description` 
        is used instead.
        """
        if self._brief is not None:
            return self._brief

        try:
            return self.description.splitlines()[0]
        except IndexError:
            return ''

    @property
    def description(self) -> str:
        """str: A detailed description of this command.
        
        If no description is set, the command's callback docstring is used instead.
        If no docstring exists, an empty string is returned.
        """
        if self._description is not None:
            return self._description

        doc = self.callback.__doc__
        if not doc:
            return ''

        return inspect.cleandoc(doc)

    @property
    def qualified_name(self) -> str:
        """str: The qualified name for this command."""
        return self.name

    @property
    def signature(self) -> str:
        """str: The signature, or "usage string" of this command.

        If :attr:`~.Command.usage` is set, it will be returned.
        Else, it is automatically generated.
        """
        return self.usage or super().signature

    def error(self, func: ErrorCallback) -> None:
        """Registers an error handler for this command.
        If no errors are raised here, the error is suppressed.
        Else, `on_command_error` is raised.

        Function signature should be of ``async (ctx: Context, error: Exception) -> Any``.
        """
        self.error_callback = func

    async def execute(self, ctx: Context, content: str) -> None:
        """|coro|

        Parses and executes this command with the given context and argument content.

        .. note::
            The prefix and command must be removed from content before-hand.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The context to invoke this command with.
        content: str
            The content of the arguments to parse.
        """
        try:
            ctx.callback, _, _ = await self._parse(content, ctx=ctx)
        except Exception as exc:
            if self.error_callback:
                try:
                    await self.error_callback(ctx, exc)
                except Exception as new_exc:
                    exc = new_exc
                else:
                    return

            ctx.bot.dispatch('command_error', ctx, exc)
        else:
            await ctx.reinvoke()

    async def invoke(self, ctx: Context, /, *args: P.args, **kwargs: P.kwargs) -> None:
        """|coro|

        Invokes this command with the given context.

        Parameters
        ----------
        ctx: :class:`~.Context`
            The context to invoke this command with.
        *args
            The positional arguments to pass into the callback.
        **kwargs
            The keyword arguments to pass into the callback.
        """
        try:
            ctx.bot.dispatch('command', ctx)
            await ctx.callback(ctx, *args, **kwargs)
        except Exception as exc:
            if self.error_callback:
                try:
                    await self.error_callback(ctx, exc)
                except Exception as new_exc:
                    exc = new_exc
                else:
                    return

            ctx.bot.dispatch('command_error', ctx, exc)
        else:
            ctx.bot.dispatch('command_success', ctx)
        finally:
            ctx.bot.dispatch('command_complete', ctx)


class Context:
    """Represents the context for when a command is invoked.

    Attributes
    ----------
    bot: :class:`~.Bot`
        The bot that created this context.
    message: :class:`~.Message`
        The message that invoked this context.
    prefix: str
        The prefix used to invoke this command.
        Could be, but rarely is ``None``.
    invoked_with: str
        The command name used to invoke this command.
        This could be used to determine which alias invoked this command.
        Could be ``None``.
    command: :class:`~.Command`
        The command invoked. Could be ``None``.
    callback: Callable
        The parsed command callback that will be used. Could be ``None``.
    args: tuple
        The arguments used to invoke this command. Could be ``None``.
    kwargs: Dict[str, Any]
        The keyword arguments used to invoke this command. Could be ``None``.
    reader: :class:`~.StringReader`
        The string-reader that was used to parse this command. Could be ``None``.
    """

    def __init__(self, bot: Bot, message: Message) -> None:
        self.bot: Bot = bot
        self.message: Message = message

        self.prefix: Optional[str] = None
        self.invoked_with: Optional[str] = None

        self.command: Optional[Command] = None
        self.callback: Optional[CommandCallback] = None
        self.args: Optional[tuple] = None
        self.kwargs: Optional[Dict[str, Any]] = None
        self.reader: Optional[StringReader] = None

        self.send: Optional[Callable[[str], Message]] = getattr(self.channel, 'send', None)

    def __repr__(self) -> str:
        return f'<Context command={self.command!r}>'

    async def invoke(self, command: Command[P, Any], /, *args: P.args, **kwargs: P.kwargs) -> None:
        """|coro|

        Invokes the given command with this context.

        .. note:: No checks will be called here.

        Parameters
        ----------
        command: :class:`~.Command`
            The context to invoke this command with.
        *args
            The positional arguments to pass into the callback.
        **kwargs
            The keyword arguments to pass into the callback.
        """
        self.command = command
        self.args = args
        self.kwargs = kwargs

        await command.invoke(self, *args, **kwargs)

    async def reinvoke(self) -> None:
        """|coro|

        Re-invokes this command with the same arguments.

        .. note:: No checks will be called here.
        """
        await self.invoke(self.command, *self.args, **self.kwargs)
    
    @property
    def channel(self) -> Optional[Channel]:
        """Optional[:class:`~.Channel`]: The channel that this context was invoked in."""
        return self.message.channel
    
    @property
    def author(self) -> Optional[User]:
        """Optional[:class:`~.User`]: The user that this context was invoked by."""
        return self.message.author
    
    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`~.Guild`]: The guild that this context was invoked in."""
        return self.message.guild
    
