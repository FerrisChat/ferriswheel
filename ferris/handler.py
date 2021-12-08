from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Coroutine, Optional

from .channel import Channel
from .guild import Guild
from .member import Member
from .message import Message
from .user import ClientUser, User
from .role import Role
from .invite import Invite

if TYPE_CHECKING:
    from .connection import Connection
    from .websocket import KeepAliveManager

log = logging.getLogger(__name__)


class _BaseEventHandler:
    def __init__(
        self, connection: Connection, heartbeat_manager: KeepAliveManager
    ) -> None:
        self.connection: Connection = connection
        self.dispatch: Coroutine = connection.dispatch

        self._heartbeat_manager: KeepAliveManager = heartbeat_manager

    def handle(self, _data: dict):
        event = _data.get('c')
        data = _data.get('d')
        log.debug(f"Handling event: {event} Data: {data}")

        self.dispatch('socket_receive', event, data)

        try:
            asyncio.create_task(getattr(self, event)(data))
        except AttributeError:
            log.error(f'Received unkwown event: {event}')


class EventHandler(_BaseEventHandler):
    async def IdentifyAccepted(self, data):
        self.dispatch('identify_accepted')

        u = ClientUser(self.connection, data.get('user', {}))
        self.connection.store_user(u)

        self.connection._user = u

        self.connection._is_ready.set_result(None)
        self.dispatch('ready')

        self.connection._is_ready = self.connection.loop.create_future()

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

        self.dispatch('message_update', old, new)

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

        self.connection.get_guild(c.guild_id)._channels.pop(c.id, None)

    async def MemberCreate(self, data):
        guild: Guild = self.connection.get_guild(data.get('guild_id'))
        if not guild:
            return

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

    async def GuildCreate(self, data):
        g = Guild(self.connection, data.get('guild'))

        self.connection.store_guild(g)

        self.dispatch('guild_create', g)

    async def GuildUpdate(self, data):
        old = Guild(self.connection, data.get('old'))
        if new := self.connection.get_guild(old.id):
            new._process_data(data.get('new'))
        else:
            new = Guild(self.connection, data.get('new'))
            self.connection.store_guild(new)

        self.dispatch('guild_update', old, new)

    async def GuildDelete(self, data):
        g = Guild(self.connection, data.get('guild'))
        self.connection._guilds.pop(g.id, None)

        self.dispatch('guild_delete', g)

    async def InviteCreate(self, data):
        invite = Invite(self.connection, data.get('invite'))

        self.dispatch('invite_create', invite)

    async def InviteDelete(self, data):
        invite = Invite(self.connection, data.get('invite'))

        self.dispatch('invite_delete', invite)

    async def RoleCreate(self, data):
        r = data.get('role')
        guild: Guild = self.connection.get_guild(r.get('guild_id'))
        if role := guild._roles.get(r.get('id')):
            role._process_data(r)
        else:
            role = Role(self.connection, r)
            guild._roles[role.id] = role

        self.dispatch('role_create', role)

    async def RoleUpdate(self, data):
        old = Role(self.connection, data.get('old'))
        r = data.get('new')
        guild: Guild = self.connection.get_guild(r.get('guild_id'))
        if role := guild._roles.get(r.get('id')):
            role._process_data(r)
        else:
            role = Role(self.connection, r)
            guild._roles[role.id] = role

        self.dispatch('role_update', old, role)

    async def RoleDelete(self, data):
        r = data.get('role')
        guild: Guild = self.connection.get_guild(r.get('guild_id'))
        if role := guild._roles.get(r.get('id')):
            guild._roles.pop(role.id, None)
        else:
            role = Role(self.connection, r)
        self.dispatch('role_delete', role)

    async def TypingStart(self, data):
        c = data.get('channel')
        u = data.get('user')

        channel: Optional[Channel] = self.connection.get_channel(c.get('id'))
        if channel:
            channel._process_data(c)

        user: Optional[User] = self.connection.get_user(u.get('id'))
        if user:
            user._process_data(u)

        self.dispatch('typing_start', channel, user)

    async def TypingEnd(self, data):
        c = data.get('channel')
        u = data.get('user')

        channel: Optional[Channel] = self.connection.get_channel(c.get('id'))
        if channel:
            channel._process_data(c)

        user: Optional[User] = self.connection.get_user(u.get('id'))
        if user:
            user._process_data(u)

        self.dispatch('typing_end', channel, user)

    async def MemberRoleAdd(self, data):
        m = data.get('member')

        g = self.connection.get_guild(m.get('guild_id'))

        if member := g._members.get(m.get('user_id')):
            member._process_data(m)
        else:
            member = Member(self.connection, m)
            g._members[member.id] = member

        role = Role(self.connection, data.get('role'))

        member._roles[role.id] = role

        self.dispatch('member_role_add', member, role)

    async def MemberRoleRemove(self, data):
        m = data.get('member')

        g = self.connection.get_guild(m.get('guild_id'))

        if member := g._members.get(m.get('user_id')):
            member._process_data(m)
        else:
            member = Member(self.connection, m)
            g._members[member.id] = member

        role = Role(self.connection, data.get('role'))

        member._roles.pop(role.id, None)

        self.dispatch('member_role_remove', member, role)

    async def Ping(self, _):
        self._heartbeat_manager.pong()

    async def Pong(self, _):
        self._heartbeat_manager.ack()
