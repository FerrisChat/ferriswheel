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

        m = await c.send("Test.")
        log.info(repr(m))

        log.info("Create, Fetch channel and send message works.")

        u = await client.fetch_user(self.user.id)
        log.info(repr(u))
        log.info("Fetch user works.")

        g = await self.create_guild(name='test')

        g = await client.fetch_guild(g.id)
        log.info(repr(g))
        log.info("Create and Fetch guild works.")

        i = await g.create_invite()
        log.info(repr(i))

        log.info("Create invite works.")

        log.info("Test done, all passed")
        await self.close()


client = Client()

client.run(
    email="test.ferriswheel@ferris.chat",
    password=os.getenv('PASSWORD'),
)
