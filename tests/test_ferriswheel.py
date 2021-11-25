import asyncio
import logging
import os

import ferris

log = logging.getLogger(__name__)

_log = logging.getLogger()
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.DEBUG)


class Client(ferris.Client):
    async def on_ready(self):
        log.info("Starting test.")
        g = None
        c = None
        m = None

        async def test_guild():
            g = await self.create_guild(name='test')

            g = await self.fetch_guild(g.id)
            log.info(repr(g))
            await g.edit(name='test_edit')
            log.info("Create and Fetch and edit guild works.")
            asyncio.create_task(test_invite())
        
            c = await g.create_channel(name='test')

            c = await self.fetch_channel(c.id)
            log.info(repr(c))
            await c.edit(name='test_edit')

            m = await c.send("Test.")
            log.info(repr(m))
            await m.edit(content='test_edit')
            
            log.info("Create, Fetch, Edit channel, send, edit message works.")
        
        async def test_invite():
            i = await g.create_invite()
            log.info(repr(i))
            
            log.info("Create invite works.")

        async def test_user():
            u = await self.fetch_user(self.user.id)
            log.info(repr(u))
            log.info("Fetch user works.")

        async def test_delete():
            await m.delete()
            await c.delete()
            await g.delete()
            
            log.info("Delete message, channel, guild works.")

        f = await asyncio.gather(test_guild(), test_user())

        await test_delete()

        for r in f:
            if r is not None:
                raise r

        log.info("Test done, all passed")


client = Client()

client.run(token=os.getenv('TOKEN'))