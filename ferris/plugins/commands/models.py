from __future__ import annotations

from typing import (
    Any,
    Awaitable,
    Generic,
    List,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

R = TypeVar('R')

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    from ferris.channel import Channel
    from ferris.guild import Guild
    from ferris.message import Message
    from ferris.member import Member
    from ferris.user import User

    P = ParamSpec('P')
    CommandCallbackT = Callable[Concatenate['Context', P], Awaitable[R]]
else:
    P = TypeVar('P')


class Command(Generic[P, R]):
    """Represents a command.

    Attributes
    ----------
    name: str
        The name of this command.
    aliases: List[str]
        A list of aliases for this command.
    callback: Callable[Concatenate[:class:`.Context`, P], Awaitable[R]]
        The command callback for this command.
    """

    def __init__(
        self, name: str, aliases: List[str], callback: CommandCallbackT
    ) -> None:
        self.name: str = name
        self.aliases: List[str] = aliases
        self.callback: CommandCallbackT = callback
        self.on_error: Optional[Callable[[Context, Exception], Any]] = None

    def error(self, func: Callable[[Context, Exception], Any]) -> None:
        """Adds an error handler to this command.

        Example
        -------
        .. code:: python3

            @bot.command()
            async def raise_error(ctx: Context) -> None:
                int('a')  # Will raise ValueError

            @raise_error.error
            async def error_handler(ctx: Context, exc: Exception) -> None:
                if isinstance(exc, ValueError):
                    await ctx.send('Got ValueError!')
        """
        self.on_error = func

    async def invoke(self, ctx: Context, *args: P.args, **kwargs: P.kwargs) -> None:
        """Invokes this command.

        Parameters
        ----------
        ctx: :class:`.Context`
            The context to invoke the command with.
        *args: P.args
            The positional arguments to pass into the command callback.
        **kwargs: P.kwargs
            The keyword arguments to pass into the command callback.
        """
        try:
            await self.callback(ctx, *args, **kwargs)
            # dispatch `on_command` here...
        except Exception as exc:
            if self.on_error:
                try:
                    await self.on_error(ctx, exc)
                except Exception as new_exc:
                    exc = new_exc
                else:
                    return
            # dispatch `on_command_error` here...
        else:
            # dispatch `on_command_success` here...
            ...
        finally:
            # dispatch `on_command_complete` here...
            ...


class Context:
    """Represents the context for a command.

    Attributes
    ----------
    command: Optional[:class:`.Command`]
        The command invoked. May be ``None``.
    """

    def __init__(self, *, message: Message) -> None:
        self._message: Message = message
        self.command: Command = None

    @property
    def message(self) -> Message:
        """:class:`~.Message`: The invocation message for this context."""
        return self._message

    @property
    def author(self) -> Union[User, Member]:
        """Union[:class:`~.User`, :class:`~.Member`]: The author of this context."""
        return self._message.author

    @property
    def channel(self) -> Channel:
        """:class:`~.Channel`: The channel of this context."""
        return self._message.channel

    @property
    def guild(self) -> Guild:
        """:class:`~.Guild`: The guild of this context."""
        return self._message.guild
