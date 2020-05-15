import re

import aiohttp
import discord
from discord.ext import commands, tasks
import dbl
import keys
from services import ActivityService
import util
from util import checks
from database import errors
import logging

log = logging.getLogger('BitchBot' + __name__)


def must_have_activity_enabled():
    def pred(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage

        if ctx.guild.id in ctx.cog.wants_activity_tracking:
            return True

        raise commands.CheckFailure('Activity tracking must be enabled to use this command')

    return commands.check(pred)


# Tracks your activity in the guild and give them activity points for being active.
# noinspection PyIncorrectDocstring
class Stats(commands.Cog):
    """Commands related to statistics about bot and you"""

    def __init__(self, bot):
        self.bot = bot
        self.command_pattern = re.compile(rf'>[a-z]+')
        self.activity_service = ActivityService(self.bot.db)
        self.activity_bucket = commands.CooldownMapping.from_cooldown(1.0, 120.0, commands.BucketType.member)

        self.wants_activity_tracking = set()

        self.bot.loop.create_task(self.load_guilds())

        self.log_webhook = discord.Webhook.from_url(
            keys.logWebhook,
            adapter=discord.AsyncWebhookAdapter(self.bot.clientSession))

        if not keys.debug:
            self.dbl_client = dbl.DBLClient(self.bot, keys.dbl_token, autopost=False)
            self.stats_loop.start()

    async def load_guilds(self):
        self.wants_activity_tracking = set(await self.activity_service.get_guilds_with_tracking_enabled())

    def cog_unload(self):
        self.stats_loop.cancel()

    @commands.Cog.listener()
    async def on_regular_human_message(self, message):
        if message.guild is None:
            return  # no activity tracking in DMs

        if message.guild.id in self.wants_activity_tracking:
            if not self.activity_bucket.update_rate_limit(message):  # been two minutes since last update
                increment_by = 2
                await self.activity_service.increment(message.author.id, message.guild.id, increment_by)
                log.debug(f'Incremented activity of {message.author} ({message.author.id}) '
                          f'in {message.guild} ({message.guild.id}) by {increment_by}')

    @commands.group()
    async def stats(self, ctx):
        """Command group for stats related commands"""
        pass

    @stats.command(name='websocket', aliases=['ws'])
    async def ws_stats(self, ctx):
        """Gives stats about bot's received websocket events"""

        embed = discord.Embed(title='Websocket events received by the bot', color=util.random_discord_color())
        socket_stats = self.bot.socket_stats
        for event_name in sorted(socket_stats, key=socket_stats.get, reverse=True):
            embed.add_field(name=event_name, value=socket_stats[event_name], inline=False)

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @must_have_activity_enabled()
    async def activity(self, ctx, target: discord.Member = None):
        """
        Shows activity on the server's leaderboard

         Args:
            target: The member whose activity you want to see. Author's activity is shown if omitted
        """
        if target is None:
            target = ctx.author
        try:
            fetched = await self.activity_service.get(target)
            member = ctx.guild.get_member(fetched.user_id)
            embed = discord.Embed(color=util.random_discord_color())
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)
            embed.add_field(name='Activity Points', value=fetched.points)
            embed.add_field(name='Position', value=fetched.position)
            embed.set_footer(text='Last updated at')
            embed.timestamp = fetched.last_updated_time
            await ctx.send(embed=embed)
        except errors.NotFound:
            await ctx.send(f'Activity for user `{util.format_human_readable_user(target)}` not found')

    @activity.command(name='top')
    @must_have_activity_enabled()
    async def top_users(self, ctx, amount=10):
        """Shows top users in server's activity leaderboard"""
        fetched = await self.activity_service.get_top(guild=ctx.guild, limit=amount)
        data = []
        length = 0
        for activity in fetched:
            member = ctx.guild.get_member(activity.user_id)
            line = f'{activity.position}. {member.display_name} - {activity.points} points'
            data.append(line)
            if length < len(line):
                length = len(line)

        data.append('\n')
        data.append('-' * length)
        # I probably should use one query but I don't know how to do it so we just gonna go with two
        me = await self.activity_service.get(ctx.author)
        data.append(f'You have {me.points} points')

        await util.BloodyMenuPages(util.TextPagesData(data)).start(ctx)

    @activity.command(name='enable')
    @commands.guild_only()
    @checks.can_config()
    async def activity_enable(self, ctx):
        await self.activity_service.set_tracking_state(ctx.guild.id, True)
        self.wants_activity_tracking.add(ctx.guild.id)

        await ctx.send('Activity tracking has been enabled')

    @activity.command(name='disable')
    @commands.guild_only()
    @checks.can_config()
    async def activity_disable(self, ctx):
        await self.activity_service.set_tracking_state(ctx.guild.id, False)
        self.wants_activity_tracking.remove(ctx.guild.id)

        await ctx.send('Activity tracking has been disabled')

    @tasks.loop(minutes=60)
    async def stats_loop(self):
        if keys.debug:
            return

        log.info("Posting stats")
        await self.dbl_client.post_guild_count()
        session: aiohttp.ClientSession = self.bot.clientSession
        await session.post(
            'https://listmybots.com/api/public/bot/stats',
            json={'server_count': len(self.bot.guilds)},
            headers={'Authorization': keys.list_my_bots_token})

        await session.post(
            f'https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats',
            json={'guildCount': len(self.bot.guilds)},
            headers={'Authorization': keys.dbots_token})

        await session.post(
            f'https://api.discordapps.dev/api/v2/bots/{self.bot.user.id}',
            json={"bot": {"count": len(self.bot.guilds)}},
            headers={'Authorization': keys.discordapps_token})

        await self.log_webhook.send('Posted stats')
        log.info("Successfully posted stats")

    @stats_loop.before_loop
    async def before_stats_loop(self):
        self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Stats(bot))
