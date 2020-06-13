import asyncio
import logging
import sys
import traceback

import aiohttp
import discord
from discord.ext import commands
from util import commands as bloody_commands, database, lavalink
import keys
from jishaku.paginators import WrappedPaginator
import util
import random
import hypercorn
import os

from services import ConfigService
from web.backend.utils.quart_with_bot import QuartWithBot

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


async def before_invoke(ctx: bloody_commands.Context):
    if getattr(ctx.command, 'wants_db', False):
        # Thanks to circular imports
        # noinspection PyUnresolvedReferences
        ctx.db = await ctx.bot.db.acquire()


async def after_invoke(ctx: bloody_commands.Context):
    if ctx.db is not None:
        await ctx.db.close()


class BlacklistedUserInvoked(commands.CheckFailure):
    pass


async def global_check(ctx: bloody_commands.Context):
    # noinspection PyUnresolvedReferences
    if ctx.message.author.id in ctx.bot.blacklist:
        raise BlacklistedUserInvoked()
    return True


# noinspection PyMethodMayBeStatic
class BitchBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=_prefix_pred,
            help_command=util.BloodyHelpCommand(),
            owner_id=529535587728752644,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
            status=discord.Status.online,
            activity=discord.Game(f"use >help or @mention me")
        )
        self.loop = self.loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession()

        self.quart_app = QuartWithBot(__name__, static_folder=None)
        self.quart_app.debug = keys.debug
        # Probably should put it with config
        self.initial_cogs = kwargs.pop('cogs')

        # socket stats props
        self.socket_stats = {}

        # self.lines_of_code_count = self._count_lines_of_code()
        self.lines_of_code_count = 0

        self.prefixes = {}

        self.blacklist = {}
        self.blacklist_message_bucket = commands.CooldownMapping.from_cooldown(1, 15.0, commands.BucketType.user)

        self.log_webhook = discord.Webhook.from_url(keys.logWebhook,
                                                    adapter=discord.AsyncWebhookAdapter(self.session))

        self._before_invoke = before_invoke
        self._after_invoke = after_invoke
        self.add_check(global_check)

    # noinspection PyMethodMayBeStatic,SpellCheckingInspection
    async def setup_logger(self):
        discord_handler = util.DiscordLoggingHandler(self.loop, self.session)

        dpy_logger = logging.getLogger('discord')
        dpy_logger.setLevel(logging.INFO)
        dpy_logger.addHandler(file_handler)
        # dpy_logger.addHandler(discord_handler)

        bitch_bot_logger.addHandler(discord_handler)

    async def set_prefix(self, db, prefix, *, should_insert=True):
        if should_insert:
            prefix = await ConfigService.insert_prefix(db, prefix)

        self.prefixes[prefix.guild_id] = str(prefix)

        return prefix

    async def clear_custom_prefix(self, db, guild_id):
        await ConfigService.delete_prefix(db, guild_id)
        del self.prefixes[guild_id]

    # noinspection PyAttributeOutsideInit
    async def start(self, *args, **kwargs):

        await self.setup_logger()

        self.db = await database.init(self.loop)

        self.load_extension('util.timers')

        for cog_name in self.initial_cogs:
            try:
                self.load_extension(f"cogs.{cog_name}")
                bitch_bot_logger.debug(f'Successfully loaded extension {cog_name}')
            except Exception as e:
                bitch_bot_logger.exception(f'Failed to load loaded extension {cog_name}', e)

        for i in ('spa_serve', 'routes', 'commands', 'webhooks'):
            self.load_extension(f'web.backend.routes.{i}')

        async with self.db.acquire() as db:
            prefixes = await ConfigService.get_all_prefixes(db)
        for i in prefixes:
            await self.set_prefix(db=None, prefix=i, should_insert=False)

        async with self.db.acquire() as db:
            blacklist = await ConfigService.get_blacklisted_users(db)
        for blocked_user in blacklist:
            self.blacklist[blocked_user.user_id] = blocked_user

        self.lavalink = lavalink.Client(keys.client_id)
        self.lavalink.add_node('127.0.0.1', 2333, keys.lavalink_pass, 'eu', 'debug-node')
        self.add_listener(self.lavalink.voice_update_handler, 'on_socket_response')

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
        await self.session.close()
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

        await self.log_webhook.send(embed=embed)

    async def on_message(self, message):
        if message.author.bot:  # don't do anything if the author is a bot
            return

        ctx = await self.get_context(message, cls=bloody_commands.Context)

        if not ctx.valid:
            if self.user.mentioned_in(message) \
                    and (message.guild is not None and message.channel.permissions_for(message.guild.me).send_messages):

                await message.channel.send(random.choice(  # :pinng:
                    ["<a:ping:610784135627407370>", "<a:pinng:689843900889694314>"]))
                if message.guild.get_member(self.owner_id) is not None:
                    await self.send_ping_log_embed(message)  # and log the message

            self.dispatch('regular_human_message', message)

        await self.invoke(ctx)

    async def on_ready(self):
        print(f"{self.user.name} is running")
        print("-" * len(self.user.name + " is running"))

    async def on_socket_response(self, msg):
        event = msg['t']
        if event is None:
            return
        try:
            self.socket_stats[event] += 1
        except KeyError:
            self.socket_stats[event] = 1

    async def on_command_error(self, ctx: commands.Context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

        if isinstance(exception, BlacklistedUserInvoked):
            if (ctx.message.channel.permissions_for(ctx.message.guild.me).send_messages and
                    not self.blacklist_message_bucket.update_rate_limit(ctx.message)):

                blacklist = self.blacklist[ctx.message.author.id]

                embed = discord.Embed(
                    title='You have been blocked from using this bot by the bot owner',
                    timestamp=blacklist.blacklisted_at,
                    color=discord.Color.red()
                ).set_footer(text='Blocked at')

                if blacklist.reason:
                    embed.description = f'**Reason**: {blacklist.reason}'

                return await ctx.send(embed=embed)

        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)

        async def send(msg):
            await ctx.send(
                embed=discord.Embed(
                    description=f'{str(msg)}\n'
                                f'See `{ctx.prefix}help {ctx.command.qualified_name}` for more info or '
                                f'join the [support server]({util.SUPPORT_SERVER_INVITE}) for help',
                    color=discord.Color.red()),
                allowed_mentions=allowed_mentions)

        if isinstance(exception, (commands.CheckFailure, commands.UserInputError, commands.MaxConcurrencyReached)):
            return await send(exception)

        exception = getattr(exception, 'original', exception)

        if isinstance(exception, discord.Forbidden):
            if not ctx.channel.permissions_for(ctx.author).send_messages:
                return
            return await send(exception)
        else:
            await send(f'{exception.__class__.__name__} : {str(exception)}')

            tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__, 5))
            sp = util.space
            embed = discord.Embed(
                title=f'{exception.__class__.__name__} : {str(exception)}',
                description=f'**Message**:\n'
                            f'{sp(2)}**Content**: {ctx.message.content}\n'
                            f'{sp(2)}**ID**: {ctx.message.id}\n'
                            f'{sp(2)}**Author**: {ctx.author}\n'
                            f'{sp(2)}**Author\'s ID**: {ctx.author.id}\n'
                            f'**Guild**:\n'
                            f'{sp(2)}**Name**: {ctx.guild.name}\n'
                            f'{sp(2)}**ID**: {ctx.guild.id}\n'
                            f'{sp(2)}**Owner in guild**: {ctx.guild.get_member(self.owner_id) is not None}\n'
                            f'**Traceback**: {tb}',
                color=discord.Color.red()
            )

            await self.log_webhook.send(embed=embed)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def on_guild_join(self, guild):
        sp = util.space
        perms = util.user_presentable_perms(guild.me.guild_permissions).split('\n')

        embed = discord.Embed(
            title=f"I just joined a server {'<:weebyay:676427364871307285> ' * 3}",
            color=util.random_discord_color(),
            description=f'**Name**: {guild}\n'
                        f'**ID**: {guild.id}\n'
                        f'**Owner**: {guild.owner} ({guild.owner.id})\n'
                        f'**Members**:\n'
                        f'{sp(2)}**Total**: {guild.member_count}\n'
                        f'{sp(2)}**Bots**: {len([m for m in guild.members if m.bot])}\n'
                        f'**Permissions**:\n'
                        f'{sp(2)}**Allowed**: {perms[1]}\n'
                        f'{sp(2)}**Denied**: {"None" if len(perms) == 3 else perms[3]}\n'
                        f'**Current guild count**: {len(self.guilds)}'
        )
        embed.set_thumbnail(url=guild.icon_url)

        if len(guild.emojis) != 0:
            pg = WrappedPaginator(prefix='', suffix='', max_size=1024)
            pg.add_line(' '.join(map(str, guild.emojis)))
            first = True
            for page in pg.pages:
                if first:
                    embed.add_field(name='Emojis', value=f"{page}", inline=False)
                    first = False
                else:
                    embed.add_field(name='\u200b', value=f"{page}", inline=False)
        else:
            embed.add_field(name='Emojis', value=f"None", inline=False)

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
            with open(file, encoding='utf-8') as f:
                read_file = f.read().split('\n')
                lines = [x for x in read_file if x != '']
                lines_count += len(lines)

        return lines_count

    def refresh_loc_count(self):
        self.lines_of_code_count = self._count_lines_of_code()

    async def refresh_prefixes(self, db):
        self.prefixes.clear()
        prefixes = await ConfigService.get_all_prefixes(db)
        for i in prefixes:
            await self.set_prefix(db=None, prefix=i, should_insert=False)

    async def blacklist_user(self, db, user, *, reason=None):
        blacklisted = await ConfigService.blacklist_user(db, user.id, reason=reason)
        self.blacklist[blacklisted.user_id] = blacklisted

    async def remove_from_blacklist(self, db, user):
        await ConfigService.remove_user_from_blacklist(db, user.id)
        del self.blacklist[user.id]
