import asyncio
import logging
import aiohttp
import discord
from discord.ext import commands

from jishaku.paginators import WrappedPaginator
from database import database
import util
import random
import hypercorn
import os
import dbl

from services import ActivityService, ConfigService
from util.monkeypatches import *
from quart.local import LocalProxy

bitch_bot_logger = logging.getLogger('BitchBot')
bitch_bot_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
fmt = '%(name)s: %(levelname)s: %(asctime)s: %(message)s'
file_handler.setFormatter(logging.Formatter(fmt))
bitch_bot_logger.addHandler(file_handler)


async def _prefix_pred(bot, message):
    prefixes = []
    try:
        prefixes.append(bot.prefixes[message.guild.id])
    except (KeyError, AttributeError):
        prefixes.append('>')

    return commands.when_mentioned_or(*prefixes)(bot, message)


# noinspection PyMethodMayBeStatic
class BitchBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=_prefix_pred,
            help_command=util.BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
        )
        LocalProxy.bot = self
        self.quart_app = util.QuartWithBot(__name__, static_folder=None)
        self.quart_app.config['SECRET_KEY'] = keys.client_secret
        self.quart_app.debug = keys.debug
        # Probably should put it with config
        self.initial_cogs = kwargs.pop('cogs')

        # socket stats props
        self.socket_stats = {}

        self.lines_of_code_count = self._count_lines_of_code()

        self.prefixes = {}

        self.blacklist = {}
        self.blacklist_message_bucket = commands.CooldownMapping.from_cooldown(1.0, 15.0, commands.BucketType.user)

        if not keys.debug:
            self.dbl_client = dbl.DBLClient(self, keys.dbl_token, autopost=True)

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    async def setup_logger(self):
        discord_handler = util.DiscordLoggingHandler(self.loop, self.clientSession)

        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.INFO)
        dpy_logger.addHandler(file_handler)
        dpy_logger.addHandler(discord_handler)

        bitch_bot_logger.addHandler(discord_handler)

    async def set_prefix(self, prefix, *, should_insert=True):
        if should_insert:
            prefix = await self.config_service.insert_prefix(prefix)

        self.prefixes[prefix.guild_id] = str(prefix)

        return prefix

    async def clear_custom_prefix(self, guild_id):
        await self.config_service.delete_prefix(guild_id)
        del self.prefixes[guild_id]

    # noinspection PyAttributeOutsideInit
    async def start(self, *args, **kwargs):
        self.clientSession = aiohttp.ClientSession()

        await self.setup_logger()

        self.db = await database.init(self.loop)

        self.load_extension('util.timers')

        self.activity_service = ActivityService(self.db)
        self.config_service = ConfigService(self.db)

        for cog_name in self.initial_cogs:
            try:
                self.load_extension(f"cogs.{cog_name}")
                bitch_bot_logger.debug(f'Successfully loaded extension {cog_name}')
            except Exception as e:
                bitch_bot_logger.exception(f'Failed to load loaded extension {cog_name}', e)

        for i in ('spa_serve', 'routes'):  # , 'user_routes', 'auth', 'mod'
            self.load_extension(f'web.backend.routes.{i}')

        prefixes = await self.config_service.get_all_prefixes()
        for i in prefixes:
            await self.set_prefix(i, should_insert=False)

        blacklist = await self.config_service.get_blacklisted_users()
        for blocked_user in blacklist:
            self.blacklist[blocked_user.user_id] = blocked_user

        await super().start(*args, **kwargs)

    def run(self, *args, **kwargs):
        async def start_quart():
            config = hypercorn.Config()
            config.bind = ["0.0.0.0:6969"]
            # noinspection PyUnresolvedReferences
            await hypercorn.asyncio.serve(self.quart_app, config)

        def done_callback(_):
            self.loop.create_task(self.close())

        future = asyncio.ensure_future(start_quart(), loop=self.loop)
        future.add_done_callback(done_callback)
        super().run(*args, **kwargs)

    async def close(self):
        await self.clientSession.close()
        await self.db.close()
        await super().close()

    async def send_ping_log_embed(self, message):
        embed = discord.Embed(title=f"{self.user.name} was mentioned in {message.guild}",
                              color=util.random_discord_color(),
                              description=f'**Message content:**\n{message.content}')
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.set_thumbnail(url=message.guild.icon_url)
        embed.add_field(name='Guild', value=f'{message.guild} ({message.guild.id})')
        embed.add_field(name='Channel', value=f'{message.channel.mention}')
        embed.add_field(name='Author', value=f'{message.author.display_name} ({message.author}; {message.author.id})')
        embed.add_field(name='Link', value=f'[Jump to message]({message.jump_url})')

        webhook = discord.Webhook.from_url(keys.logWebhook,
                                           adapter=discord.AsyncWebhookAdapter(self.clientSession))
        await webhook.send(embed=embed)

    async def on_message(self, message):
        if message.author.bot:  # don't do anything if the author is a bot
            return

        ctx = await self.get_context(message)

        if not ctx.valid:
            if self.user.mentioned_in(message) \
                    and (message.guild is not None and message.channel.permissions_for(message.guild.me)):

                await message.channel.send(random.choice(  # :pinng:
                    ["<a:ping:610784135627407370>", "<a:pinng:689843900889694314>"]))
                if message.guild.get_member(self.owner_id) is not None:
                    await self.send_ping_log_embed(message)  # and log the message

            self.dispatch('regular_human_message', message)
        else:
            if message.author.id in self.blacklist:  # handle blacklist
                if message.channel.permissions_for(message.guild.me).send_messages and \
                        not self.blacklist_message_bucket.update_rate_limit(message):
                    blacklist = self.blacklist[message.author.id]
                    reason = blacklist.reason if blacklist.reason is not None else "No reason provided"
                    embed = discord.Embed(title='You have been blocked from using this bot by the bot owner',
                                          description=f'**Reason**: {reason}',
                                          timestamp=blacklist.blacklisted_at)
                    embed.set_footer(text='Blocked at')

                    await message.channel.send(embed=embed)

                return

        await self.invoke(ctx)

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"use >help or @mention me")
        )

    async def on_socket_response(self, msg):
        event = msg['t']
        if event is None:
            return
        try:
            self.socket_stats[event] += 1
        except KeyError:
            self.socket_stats[event] = 1

    async def on_command_error(self, ctx: commands.Context, exception):
        exception = getattr(exception, 'original', exception)

        if isinstance(exception, commands.CheckFailure):
            await ctx.send(str(exception))
        elif isinstance(exception, commands.UserInputError):
            msg = f'See `{ctx.prefix}help {ctx.command.qualified_name}` for more info'
            await ctx.send('\n'.join([str(exception), msg]))
        elif isinstance(exception, commands.CommandNotFound):
            pass
        else:
            await ctx.send(f'{exception.__class__.__name__}: {str(exception)}')
            bitch_bot_logger.exception(f'{exception}\nMessage:{ctx.message.jump_url}')

    async def on_guild_join(self, guild):

        embed = discord.Embed(title=f"'{self.user.name} just joined a server {':weebyay:676427364871307285' * 3}'",
                              color=util.random_discord_color())
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name='Guild', value=f'{guild} ({guild.id})')
        embed.add_field(name='Owner', value=f'{guild.owner} ({guild.owner.id})')
        embed.add_field(name='Member count',
                        value=f'{guild.member_count} ({len([m for m in guild.members if m.bot])} bots)')
        embed.add_field(name='Current guild count', value=f'{len(self.guilds)}')

        pg = WrappedPaginator(prefix='', suffix='', max_size=1024)
        pg.add_line(' '.join(map(str, guild.emojis)))
        first = True
        for page in pg.pages:
            if first:
                embed.add_field(name='Emojis', value=f"{page}", inline=False)
                first = False
            else:
                embed.add_field(name='\u200b', value=f"{page}", inline=False)

        await self.get_channel(648069341341810688).send(embed=embed)

    def get_mutual_guilds(self, member_id):
        for guild in self.guilds:
            if member_id in [x.id for x in guild.members]:
                yield guild

    def _get_all_files(self):
        for root, dirs, files in os.walk("."):
            if root.startswith(('./venv', './web/frontend/node_modules', '.git', '.idea')):
                continue
            for file in files:
                if file.endswith(('.py',)):
                    yield os.path.join(root, file)

    def _count_lines_of_code(self):
        all_files = list(self._get_all_files())
        lines_count = 0
        for file in all_files:
            with open(file) as f:
                read_file = f.read().split('\n')
                lines = [x for x in read_file if x != '']
                lines_count += len(lines)

        return lines_count

    def refresh_loc_count(self):
        self.lines_of_code_count = self._count_lines_of_code()

    async def refresh_prefixes(self):
        self.prefixes.clear()
        prefixes = await self.config_service.get_all_prefixes()
        for i in prefixes:
            await self.set_prefix(i, should_insert=False)

    async def blacklist_user(self, user, *, reason=None):
        blacklisted = await self.config_service.blacklist_user(user.id, reason=reason)
        self.blacklist[blacklisted.user_id] = blacklisted

    async def remove_from_blacklist(self, user):
        await self.config_service.remove_user_from_blacklist(user.id)
        del self.blacklist[user.id]
