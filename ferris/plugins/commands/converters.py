from __future__ import annotations

from typing import TYPE_CHECKING

from ...errors import NotFound
from ...utils import INVITE_REGEX, find
from .errors import BadArgument

if TYPE_CHECKING:
    from ... import Channel, Guild, Invite, Member, Message, Role, User
    from .models import Context
    from .parser import Converter

class ChannelConverter(Converter[Channel]):
    async def convert(self, ctx: Context, argument: str):
        c = None

        if argument.isdigit():
            id_ = int(argument)

            c = ctx.bot.get_channel(id_)

            if not c:
                try:
                    c = await ctx.bot.fetch_channel(id_)
                except NotFound:
                    if not c:
                        raise BadArgument(f'Channel {id_!r} not found')
        else:
            raise BadArgument(f'Argument must be an id.')
        
        return c


class GuildConverter(Converter[Guild]):
    async def convert(self, ctx: Context, argument: str):
        g = None

        if argument.isdigit():
            id_ = int(argument)

            g = ctx.bot.get_guild(id_)

            if not g:
                try:
                    g = await ctx.bot.fetch_guild(id_)
                except NotFound:
                    if not g:
                        raise BadArgument(f'Guild {id_!r} not found')
        else:
            raise BadArgument(f'Argument must be an id.')
        
        return g


class UserConverter(Converter[User]):
    async def convert(self, ctx: Context, argument: str):
        u = None

        if argument.isdigit():
            id_ = int(argument)

            u = ctx.bot.get_user(id_)

            if not u:
                try:
                    u = await ctx.bot.fetch_user(id_)
                except NotFound:
                    if not u:
                        raise BadArgument(f'User {id_!r} not found')
        else:
            raise BadArgument(f'Argument must be an id.')
        
        return u


class MemberConverter(Converter[Member]):
    async def convert(self, ctx: Context, argument: str):
        m = None
        
        if argument.isdigit():
            id_ = int(argument)
        
            m = ctx.guild.get_member(id_)

            if not m:
                try:
                    m = await ctx.guild.fetch_member(id_)
                except NotFound:
                    raise BadArgument(f'Member {id_!r} not found')
        else:
            raise BadArgument('Argument must be an id.')
        
        return m


class MessageConverter(Converter[Message]):
    async def convert(self, ctx: Context, argument: str):
        m = None

        if argument.isdigit():
            id_ = int(argument)

            m = ctx.bot.get_message(id_)

            if not m:
                try:
                    m = await ctx.bot.fetch_message(id_)
                except NotFound:
                    raise BadArgument(f'Message {id_!r} not found')
        else:  # TODO: Convert from message url after webclient rewrite
            raise BadArgument('Argument must be an id.')
        
        return m


class RoleConverter(Converter[Role]):
    async def convert(self, ctx: Context, argument: str):
        r = None

        if argument.isdigit():
            id_ = int(argument)

            r = ctx.guild.get_role(id_)

            if not r:
                try:
                    r = await ctx.guild.fetch_role(id_)
                except NotFound:
                    raise BadArgument(f'Role {id_!r} not found')
        else:
            r = find(lambda r: r.name == argument, ctx.guild.roles)
            
            if not r:
                raise BadArgument('Argument must be role id or name.')
        
        return r


class InviteConverter(Converter[Invite]):
    async def convert(self, ctx: Context, argument: str):
        match = INVITE_REGEX.match(argument)

        if match:
            argument = match.group(4)
        
        try:
            i =  await ctx.bot.fetch_invite(argument)
            return i
        except NotFound:
            raise BadArgument('Argument must be a valid invite url or code.')
