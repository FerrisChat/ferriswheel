from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Dict, Generator, TYPE_CHECKING, Sequence, Union

from ferris.client import Client
from .models import Command

if TYPE_CHECKING:
    from ferris.message import Message

    _BasePrefixT = Union[str, Sequence[str]]
    PrefixT = Union[
        _BasePrefixT,
        Callable[['Bot', Message], Union[_BasePrefixT, Awaitable[_BasePrefixT]]],
    ]


class CommandSink:
    """Represents a sink of commands.
    This will both mixin to :class:`.Bot` and :class:`.CommandGroup`.

    Attributes
    ----------
    mapping: Dict[str, :class:`.Command`]
        A full mapping of command names to commands.
    """

    def __init__(self) -> None:
        self.mapping: Dict[str, Command] = {}

    def walk_commands(self) -> Generator[Command]:
        """Returns a generator that walks through all of the commands
        this sink holds.

        Returns
        -------
        Generator[:class:`.Command`]
        """
        seen = set()
        for command in self.mapping.values():
            if command not in seen:
                seen.add(command)
                yield command

    @property
    def commands(self) -> None:
        """List[:class:`.Command`]: A list of the commands this sink holds."""
        return list(self.walk_commands())


class Bot(Client, CommandSink):
    """Represents a client connection to Discord with extra command handling support.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The event loop to use for the client. If not passed, then the default event loop is used.
    prefix
        The prefix the bot will listen for. This is required.
    max_messages_count: Optional[int]
        The maximum number of messages to store in the internal message buffer.
        Defaults to ``1000``.
    """

    def __init__(self, prefix: PrefixT, **kwargs) -> None:
        super().__init__(**kwargs)
        CommandSink.__init__(self)

        self.prefix: PrefixT = prefix
