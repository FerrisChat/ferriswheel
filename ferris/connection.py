from asyncio import AbstractEventLoop
from collections import deque
from typing import Dict

from .guild import Guild
from .http import HTTPClient
from .message import Message
from .user import User


class Connection:
    def __init__(self, loop: AbstractEventLoop, /, **options) -> None:
        self.api: HTTPClient = None
        self.__token: str = None

        self._max_messages_count: int = options.get("max_messages_count", 1000)

        self._clear_store()

    def _store_token(self, token: str, /) -> None:
        self.__token = token

    def _initialize_http(self, token: str, /) -> None:
        self.api = HTTPClient(token)
        self._store_token(token)

    def _clear_store(self, /) -> None:
        self._users: Dict[int, User] = {}
        self._guilds: Dict[int, Guild] = {}

        self._messages: deque = deque(maxlen=self._max_messages_count)

    def _store_message(self, message, /) -> None:
        self._messages.append(message)

    def _store_user(self, user: User, /) -> None:
        self._users[user.id] = user

    def _store_guild(self, guild: Guild, /) -> None:
        self._guilds[guild.id] = guild
