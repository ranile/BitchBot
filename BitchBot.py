import logging

import aiohttp
import discord
from discord.ext import commands

from database import database
from util import BloodyHelpCommand, Timers, DiscordLoggingHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
fmt = '%(name)s: %(levelname)s: %(asctime)s: %(message)s'
file_handler.setFormatter(logging.Formatter(fmt))
logger.addHandler(file_handler)


class BitchBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or('>'),
            help_command=BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
        )

        # self.tornado_app = tornado.web.Application(
        #     [(route, handler, dict(bot=self)) for route, handler in routes], **{
        #         'debug': True
        #     })

        self.initial_cogs = kwargs.pop('cogs')

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    async def setup_logger(self):
        discord_handler = DiscordLoggingHandler(self.loop, self.clientSession)

        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.INFO)
        dpy_logger.addHandler(file_handler)
        dpy_logger.addHandler(discord_handler)

        cogs_logger = logging.getLogger('cogs')
        cogs_logger.setLevel(logging.INFO)
        cogs_logger.addHandler(file_handler)
        cogs_logger.addHandler(discord_handler)

        logger.addHandler(discord_handler)

    # noinspection PyAttributeOutsideInit
    async def start(self, *args, **kwargs):
        self.clientSession = aiohttp.ClientSession()
        await self.setup_logger()
        # self.tornado_app.listen(6969)
        self.db = await database.init(self.loop)
        self.timers = Timers(self)
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
