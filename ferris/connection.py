from __future__ import annotations

from asyncio import AbstractEventLoop
from collections import deque
from typing import TYPE_CHECKING, Dict, Optional, Any, Union

from .http import APIRouter, HTTPClient
from .utils import find

if TYPE_CHECKING:
    from .guild import Guild
    from .message import Message
    from .user import User
    from .channel import Channel


__all__ = ('Connection',)


class Connection:
    def __init__(self, loop: AbstractEventLoop, /, **options) -> None:
        self.loop: AbstractEventLoop = loop

        self._http: Union[HTTPClient, Any] = None
        self.__token: Optional[str] = None

        self._max_messages_count: int = options.get("max_messages_count", 1000)

        self.clear_store()

    @property
    def api(self) -> Union[APIRouter, Any]:
        return self._http.api if self._http else None

    def _store_token(self, token: str, /) -> None:
        self.__token = token

    def _initialize_http(self, token: str, /) -> None:
        self._http = HTTPClient(token)
        self._store_token(token)

    async def _initialize_http_with_email(
        self, email: str, password: str, id: int, /
    ) -> None:
        self._http = await HTTPClient.from_email_and_password(email, password, id)
        self._store_token(self._http.token)

    def clear_store(self, /) -> None:
        self._users: Dict[int, User] = {}
        self._guilds: Dict[int, Guild] = {}
        self._channels: Dict[int, Channel] = {}

        self._messages: deque = deque(maxlen=self._max_messages_count)

    def deref_user(self, id: int, /) -> None:
        self._users.pop(id, None)

    def deref_channel(self, id: int, /) -> None:
        self._channels.pop(id, None)

    def store_message(self, message: Message, /) -> None:
        self._messages.append(message)

    def store_user(self, user: User, /) -> None:
        self._users[user.id] = user

    def store_guild(self, guild: Guild, /) -> None:
        self._guilds[guild.id] = guild

    def store_channel(self, channel: Channel, /) -> None:
        self._channels[channel.id] = channel

    def get_message(self, id: int, /) -> Optional[Message]:
        return find(lambda m: m.id == id, self._messages)

    def get_user(self, id: int, /) -> Optional[User]:
        return self._users.get(id)

    def get_guild(self, id: int, /) -> Optional[Guild]:
        return self._guilds.get(id)

    def get_channel(self, id: int, /) -> Optional[Channel]:
        return self._channels.get(id)
