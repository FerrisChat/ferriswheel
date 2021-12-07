from __future__ import annotations

import asyncio
from asyncio import AbstractEventLoop
from collections import deque
from typing import TYPE_CHECKING, Any, Coroutine, Dict, Optional, Union

from ferris.types.base import Snowflake
from ferris.user import ClientUser

from .http import APIRouter, HTTPClient
from .utils import find

if TYPE_CHECKING:
    from .channel import Channel
    from .guild import Guild
    from .message import Message
    from .user import User


__all__ = ('Connection',)


class Connection:
    def __init__(
        self, loop: AbstractEventLoop, dispatch: Coroutine, /, **options
    ) -> None:
        self.loop: AbstractEventLoop = loop
        self._user: Optional[User] = None

        self.dispatch: Coroutine = dispatch

        self._is_ready: asyncio.Future = loop.create_future()

        self._http: Union[HTTPClient, Any] = None
        self.__token: Optional[str] = None

        self._max_messages_count: int = options.get("max_messages_count", 1000)

        self._max_heartbeat_timeout: int = options.get("max_heartbeat_timeout", 60)

        self.clear_store()

    @property
    def token(self) -> Optional[str]:
        return self.__token

    @property
    def api(self) -> Union[APIRouter, Any]:
        return self._http.api if self._http else None

    @property
    def user(self) -> Optional[ClientUser]:
        return self._user

    def _store_token(self, token: str, /) -> None:
        self.__token = token

    def _initialize_http(self, token: str, /) -> None:
        self._http: HTTPClient = HTTPClient(token)
        self._store_token(token)

    async def _initialize_http_with_email(self, email: str, password: str, /) -> None:
        self._http: HTTPClient = await HTTPClient.from_email_and_password(
            email, password
        )
        self._store_token(self._http.token)

    def clear_store(self, /) -> None:
        self._users: Dict[Snowflake, User] = {}
        self._guilds: Dict[Snowflake, Guild] = {}
        self._channels: Dict[Snowflake, Channel] = {}

        self._messages: deque = deque(maxlen=self._max_messages_count)

    def deref_user(self, id: Snowflake, /) -> None:
        self._users.pop(id, None)

    def deref_channel(self, id: Snowflake, /) -> None:
        self._channels.pop(id, None)

    def store_message(self, message: Message, /) -> None:
        self._messages.append(message)

    def remove_message(self, id: Snowflake, /) -> None:
        m = self.get_message(id)
        if not m:
            return
        self._messages.remove(m)

    def store_user(self, user: User, /) -> None:
        self._users[user.id] = user

    def store_guild(self, guild: Guild, /) -> None:
        self._guilds[guild.id] = guild

    def store_channel(self, channel: Channel, /) -> None:
        self._channels[channel.id] = channel

    def get_message(self, id: Snowflake, /) -> Optional[Message]:
        return find(lambda m: m.id == id, self._messages)

    def get_user(self, id: Snowflake, /) -> Optional[User]:
        return self._users.get(id)

    def get_guild(self, id: Snowflake, /) -> Optional[Guild]:
        return self._guilds.get(id)

    def get_channel(self, id: Snowflake, /) -> Optional[Channel]:
        return self._channels.get(id)
