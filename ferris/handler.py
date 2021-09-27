from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Coroutine

from .channel import Channel
from .guild import Guild
from .member import Member
from .message import Message
from .user import User

if TYPE_CHECKING:
    from .connection import Connection

log = logging.getLogger(__name__)


class _BaseEventHandler:
    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection
        self.dispatch: Coroutine = connection.dispatch
        self._is_ready: asyncio.Future = connection._is_ready

    def handle(self, _data: dict):
        event = _data.get('c')
        data = _data.get('d')
        log.debug(f"Handling event: {event} Data: {data}")

        try:
            asyncio.create_task(getattr(self, event)(data))
        except AttributeError:
            log.error(f'Received unkwown event: {event}')


class EventHandler(_BaseEventHandler):
    async def IdentifyAccepted(self, data):
        self.dispatch('identify_accepted')
        u = User(self.connection, data.get('user', {}))

        self.connection._user = u

        self._is_ready.set_result(None)
        self.dispatch('ready')

    async def MessageCreate(self, data):
        m = Message(self.connection, data.get('message'))
        self.dispatch('message', m)
        self.connection.store_message(m)

    async def MessageUpdate(self, data):
        old = Message(self.connection, data.get('old'))

        if new := self.connection.get_message(old.id):
            new._process_data(data.get('new'))
        else:
            new = Message(self.connection, data.get('new'))

        self.dispatch('message_edit', old, new)

    async def MessageDelete(self, data):
        if m := self.connection.get_message(data.get('id')):
            self.connection._messages.remove(m)
        else:
            m = Message(self.connection, data.get('message'))
            self.connection.remove_message(m.id)
        self.dispatch('message_delete', m)

    async def ChannelCreate(self, data):
        if c := self.connection.get_channel(data.get('id')):
            c._process_data(data.get('channel'))
        else:
            c = Channel(self.connection, data.get('channel'))
            self.connection.store_channel(c)
        self.dispatch('channel_create', c)

    async def ChannelUpdate(self, data):
        old = Channel(self.connection, data.get('old'))
        if new := self.connection.get_channel(old.id):
            new._process_data(data.get('new'))
        else:
            new = Channel(self.connection, data.get('new'))
            self.connection.store_channel(new)

        self.dispatch('channel_update', old, new)

    async def ChannelDelete(self, data):
        c = Channel(self.connection, data.get('channel'))
        self.dispatch('channel_delete', c)

        self.connection._channels.pop(c.id, None)

    async def MemberCreate(self, data):
        guild: Guild = self.connection.get_guild(data.get('guild_id'))
        if member := guild._members.get(data.get('user_id')):
            member._process_data(data.get('member'))
        else:
            member = Member(guild, data.get('member'))
            guild._members[member.id] = member
        self.dispatch('member_create', member)

    async def MemberUpdate(self, data):
        guild: Guild = self.connection.get_guild(data.get('guild_id'))
        if member := guild._members.get(data.get('user_id')):
            member._process_data(data.get('member'))
        else:
            member = Member(guild, data.get('user'))
            guild._members[member.id] = member
        self.dispatch('member_update', member)

    async def MemberDelete(self, data):
        guild: Guild = self.connection.get_guild(data.get('guild_id'))
        if member := guild._members.get(data.get('user_id')):
            guild._members.pop(member.id, None)
        else:
            member = Member(guild, data.get('member'))
        self.dispatch('member_delete', member)

    async def UserCreate(self, data):
        if u := self.connection.get_user(data.get('id')):
            u._process_data(data.get('user'))
        else:
            u = User(self.connection, data.get('user'))
            self.connection.store_user(u)
        self.dispatch('user_create', u)
