import asyncio
import logging
import aiohttp
import discord
from discord.ext import commands

import keys
from database import database
import util
from quart import Quart
from routes import blueprint
import hypercorn

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
            help_command=util.BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
        )

        # self.app = Quart(__name__)
        # self.app.register_blueprint(blueprint)

        self.initial_cogs = kwargs.pop('cogs')

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    async def setup_logger(self):
        discord_handler = util.DiscordLoggingHandler(self.loop, self.clientSession)

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

        self.db = await database.init(self.loop)
        self.timers = util.Timers(self)

        for cog_name in self.initial_cogs:
            try:
                self.load_extension(f"cogs.{cog_name}")
                logger.debug(f'Successfully loaded extension {cog_name}')
            except Exception as e:
                logger.warning(f'Failed to load loaded extension {cog_name}. Error: {e}')

        await super().start(*args, **kwargs)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        """
        async def start_quart():
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:6969"]
            await hypercorn.asyncio.serve(self.app, config)

        def done_callback(_):
            self.loop.create_task(self.close())

        future = asyncio.ensure_future(start_quart(), loop=self.loop)
        future.add_done_callback(done_callback)
        """

    async def close(self):
        await self.clientSession.close()
        await self.db.close()
        await super().close()

    async def process_commands(self, message):  # not on_message so I'm not calling `get_context` twice
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        mentions = [x.id for x in message.mentions]
        if not ctx.valid and self.user.id in mentions:
            await message.channel.send(random.choice["<a:ping:610784135627407370>", "<a:pinng:675402071083843593>"])
            embed = discord.Embed(title=f"{self.user.name} was mentioned in {message.guild}",
                                  color=util.random_discord_color(),
                                  description=f'**Message content:**\n{message.content}')
            embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            embed.set_thumbnail(url=message.guild.icon_url)
            embed.add_field(name='Guild', value=f'{message.guild} ({message.guild.id})')
            embed.add_field(name='Channel', value=f'{message.channel.mention}')
            embed.add_field(name='Author',
                            value=f'{message.author.display_name} ({message.author}; {message.author.id})')
            embed.add_field(name='Link', value=f'[Jump to message]({message.jump_url})')

            webhook = discord.Webhook.from_url(keys.logWebhook, adapter=discord.AsyncWebhookAdapter(self.clientSession))
            await webhook.send(embed=embed)

        await self.invoke(ctx)

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"use >help or @mention me")
        )
