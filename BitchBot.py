import asyncio
import logging
import signal

import aiohttp
import discord
import tornado.web
from discord.ext import commands

from database import database
# noinspection PyPep8Naming
from routes.routes import routesList as routes
from util.HelpCommand import BloodyHelpCommand

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s: %(asctime)s: %(message)s'))
logger.addHandler(handler)


class BitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='>',
            help_command=BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
        )

        self.tornado_app = tornado.web.Application([(route, handler, dict(bot=self)) for route, handler in routes], **{
            'debug': True
        })

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    def setup_logger(self):
        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.INFO)
        dpy_logger.addHandler(handler)

        cogs_logger = logging.getLogger('cogs')
        cogs_logger.addHandler(handler)

    # noinspection PyAttributeOutsideInit
    async def setup(self, **kwargs):
        self.setup_logger()
        # self.tornado_app.listen(6969)
        self.db = await database.init(self.loop)
        self.clientSession = aiohttp.ClientSession()
        cogs = kwargs.pop('cogs')
        for cog_name in cogs:
            try:
                self.load_extension(f"cogs.{cog_name}")
                logger.debug(f'Successfully loaded extension {cog_name}')
            except Exception as e:
                logger.warning(f'Failed to load loaded extension {cog_name}. Error: {e}')
        await self.start(kwargs.pop('token'))

    def run(self, token, cogs):
        try:
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.loop.stop())
        except NotImplementedError:
            pass

        async def on_loop_complete(_):
            self.loop.stop()

        future = asyncio.ensure_future(self.setup(token=token, cogs=cogs), loop=self.loop)
        future.add_done_callback(on_loop_complete)
        try:
            self.loop.run_forever()
        finally:
            future.remove_done_callback(on_loop_complete)

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"use {self.command_prefix}help")
        )
