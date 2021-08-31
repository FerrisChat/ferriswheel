import os
import logging

import ferris

log = logging.getLogger(__name__)

_log = logging.getLogger()
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.DEBUG)


class Client(ferris.Client):
    async def on_login(self):
        log.info("Starting test.")

        c = await client.fetch_channel(969269623054741111886615412736)
        log.info(repr(c))

        m = await c.send("Test.")
        log.info(repr(m))

        log.info("Fetch channel and send message works.")

        u = await client.fetch_user(969265165749451770983817936896)
        log.info(repr(u))
        log.info("Fetch user works.")

        g = await client.fetch_guild(969269623054741111886615412736)
        log.info(repr(g))
        log.info("Fetch guild works.")

        log.info("Test done, all passed")


client = Client()

client.run(
    email="test.ferriswheel@ferris.chat",
    password=os.getenv('PASSWORD'),
    id=969265165749451770983817936896,
)
