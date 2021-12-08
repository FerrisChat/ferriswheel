from ferris.errors import NotFound
from .parser import Converter, ConverterOutputT
from .models import Context
from .errors import BadArgument

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
