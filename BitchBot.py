import logging

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
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix='>',
            help_command=BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
        )

        self.tornado_app = tornado.web.Application([(route, handler, dict(bot=self)) for route, handler in routes], **{
            'debug': True
        })

        self.initial_cogs = kwargs.pop('cogs')

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    def setup_logger(self):
        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.INFO)
        dpy_logger.addHandler(handler)

        cogs_logger = logging.getLogger('cogs')
        cogs_logger.addHandler(handler)

    # noinspection PyAttributeOutsideInit
    async def start(self, *args, **kwargs):
        self.setup_logger()
        # self.tornado_app.listen(6969)
        self.db = await database.init(self.loop)
        self.clientSession = aiohttp.ClientSession()
        for cog_name in self.initial_cogs:
            try:
                self.load_extension(f"cogs.{cog_name}")
                logger.debug(f'Successfully loaded extension {cog_name}')
            except Exception as e:
                logger.warning(f'Failed to load loaded extension {cog_name}. Error: {e}')
        await super().start(*args, **kwargs)

    async def close(self):
        await self.clientSession.close()
        await self.db.close()
        await super().close()

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"use {self.command_prefix}help")
        )
