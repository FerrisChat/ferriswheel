from ferris.errors import NotFound
from .parser import Converter, ConverterOutputT
from .models import Context
from .errors import BadArgument
from ferris.utils import find

import re

class ChannelConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> ConverterOutputT:
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


class GuildConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> ConverterOutputT:
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


class UserConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> ConverterOutputT:
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


class MemberConverter(Converter):
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
            raise BadArgument('Argument must be an id')
        
        return m


class MessageConverter(Converter):
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
            raise BadArgument('Argument must be an id')
        
        return m


class RoleConverter(Converter):
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
                raise BadArgument('Argument must be role id or name')
        
        return r


class InviteConverter(Converter):
    async def convert(self, ctx: Context, argument: str):
        invite_regex = re.compile(r'(https?:\/\/)?(www\.)?(ferris\.sh|ferris\.chat\/invite)\/([A-Za-z0-9]+)')
        match = invite_regex.match(argument)

        if match:
            argument = match.group(4)
        
        try:
            i =  await ctx.bot.fetch_invite(argument)
            return i
        except NotFound:
            raise BadArgument('Argument passed must be a valid invite url or code')