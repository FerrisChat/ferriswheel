import os
import logging

import ferris

log = logging.getLogger(__name__)

_log = logging.getLogger()
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.DEBUG)


class Client(ferris.Client):
    async def on_ready(self):
        log.info("Starting test.")

        c = await self.create_channel(name='test')

        c = await client.fetch_channel(c.id)
        log.info(repr(c))
        await c.edit(name='test_edit')

        m = await c.send("Test.")
        log.info(repr(m))
        await m.edit(content='test_edit')


        log.info("Create, Fetch, Edit channel, send, edit message works.")

        u = await client.fetch_user(self.user.id)
        log.info(repr(u))
        log.info("Fetch user works.")

        g = await self.create_guild(name='test')

        g = await client.fetch_guild(g.id)
        log.info(repr(g))
        await g.edit(name='test_edit')
        log.info("Create and Fetch and edit guild works.")

        i = await g.create_invite()
        log.info(repr(i))

        log.info("Create invite works.")

        await m.delete()
        await c.delete()
        await g.delete()


        log.info("Delete message, channel, guild works.")

        log.info("Test done, all passed")
        await self.close()


client = Client()

client.run(
    email="test.ferriswheel@ferris.chat",
    password=os.getenv('PASSWORD'),
)
