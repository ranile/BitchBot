import asyncio
import logging

import aiohttp
import discord
import tornado.web
from discord.ext import commands

from database import database
# noinspection PyPep8Naming
from routes.routes import routesList as routes
from util.HelpCommand import BloodyHelpCommand


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
    def setup_discordpy_logger(self):
        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s: %(asctime)s: %(message)s'))
        dpy_logger.addHandler(handler)

    # noinspection PyAttributeOutsideInit
    async def setup(self, **kwargs):
        self.setup_discordpy_logger()
        # self.tornado_app.listen(6969)
        self.db = await database.init(self.loop)
        self.clientSession = aiohttp.ClientSession()
        cogs = kwargs.pop('cogs')
        for cog_name in cogs:
            self.load_extension(f"cogs.{cog_name}")
        await self.start(kwargs.pop('token'))

    async def stop(self, _):
        await self.logout()
        await self.loop.stop()

    def run(self, token, cogs):
        future = asyncio.ensure_future(self.setup(token=token, cogs=cogs), loop=self.loop)
        future.add_done_callback(self.stop)
        try:
            self.loop.run_forever()
        finally:
            future.remove_done_callback(self.stop)

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"use {self.command_prefix}help")
        )
