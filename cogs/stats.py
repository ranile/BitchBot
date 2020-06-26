import re
import aiohttp
import discord
from discord.ext import commands as dpy_commands, tasks
import keys
from BitchBot import BitchBot
from services import ActivityService
import util
from util import checks, commands, logging
import traceback

logger = logging.Logger.obtain(__name__)


def must_have_activity_enabled():
    def pred(ctx):
        if ctx.guild is None:
            raise dpy_commands.NoPrivateMessage

        if ctx.guild.id in ctx.cog.wants_activity_tracking:
            return True

        raise dpy_commands.CheckFailure('Activity tracking must be enabled to use this command')

    return dpy_commands.check(pred)


# Tracks your activity in the guild and give them activity points for being active.
# noinspection PyIncorrectDocstring
class Stats(dpy_commands.Cog):
    """Commands related to statistics about bot and you"""

    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot
        self.command_pattern = re.compile(rf'>[a-z]+')
        # noinspection PyTypeChecker
        self.activity_bucket = dpy_commands.CooldownMapping.from_cooldown(1, 120.0, dpy_commands.BucketType.member)

        self.wants_activity_tracking = set()

        self.bot.loop.create_task(self.load_guilds())

        self.log_webhook = discord.Webhook.from_url(
            keys.logWebhook,
            adapter=discord.AsyncWebhookAdapter(self.bot.session))

        if not keys.debug:
            self.stats_loop.start()

    async def load_guilds(self):
        async with self.bot.db.acquire() as db:
            self.wants_activity_tracking = set(await ActivityService.get_guilds_with_tracking_enabled(db))

    def cog_unload(self):
        self.stats_loop.cancel()

    @dpy_commands.Cog.listener()
    async def on_regular_human_message(self, message: discord.Message):
        if message.guild is None:
            return  # no activity tracking in DMs

        if message.guild.id in self.wants_activity_tracking:
            if not self.activity_bucket.update_rate_limit(message):  # been two minutes since last update
                increment_by = 2
                async with self.bot.db.acquire() as db:
                    await ActivityService.increment(db, message.author.id, message.guild.id, increment_by)
                await logger.debug(f'Incremented activity of {message.author} ({message.author.id}) '
                                   f'in {message.guild} ({message.guild.id}) by {increment_by}')

    @commands.group()
    async def stats(self, ctx: commands.Context):
        """Command group for stats related commands"""
        pass

    @stats.command(name='websocket', aliases=['ws'])
    async def ws_stats(self, ctx: commands.Context):
        """Gives stats about bot's received websocket events"""

        embed = discord.Embed(title='Websocket events received by the bot', color=util.random_discord_color())
        socket_stats = self.bot.socket_stats
        for event_name in sorted(socket_stats, key=socket_stats.get, reverse=True):
            embed.add_field(name=event_name, value=socket_stats[event_name], inline=False)

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, wants_db=True)
    @must_have_activity_enabled()
    async def activity(self, ctx: commands.Context, target: discord.Member = None):
        """
        Shows activity on the server's leaderboard

         Args:
            target: The member whose activity you want to see. Author's activity is shown if omitted
        """
        if target is None:
            target = ctx.author

        fetched = await ActivityService.get(ctx.db, target)

        if fetched is None:
            return await ctx.send(f'Activity for user `{util.format_human_readable_user(target)}` not found')

        member = ctx.guild.get_member(fetched.user_id)

        embed = discord.Embed(
            color=0x9CA1F7,
            description=f'**Activity points**: {fetched.points}\n'
                        f'**Position**: {fetched.position}',
            timestamp=fetched.last_updated_time
        ).set_footer(text='Last updated at').set_author(
            name=f'Activity for {member.display_name}', icon_url=member.avatar_url)

        await ctx.send(embed=embed)

    @activity.command(name='top', wants_db=True)
    @must_have_activity_enabled()
    async def top_users(self, ctx: commands.Context, amount: int = 10):
        """Shows top users in server's activity leaderboard"""
        fetched = await ActivityService.get_top(ctx.db, guild=ctx.guild, limit=amount)
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
        me = await ActivityService.get(ctx.db, ctx.author)
        data.append(f"You have {f'{me.points} points' if me is not None else 'no activity'}")

        await util.BloodyMenuPages(util.TextPagesData(data)).start(ctx)

    @activity.command(name='enable', wants_db=True)
    @dpy_commands.guild_only()
    @checks.can_config()
    async def activity_enable(self, ctx: commands.Context):
        """Enable activity tracking for this server"""

        await ActivityService.set_tracking_state(ctx.db, ctx.guild.id, True)
        self.wants_activity_tracking.add(ctx.guild.id)

        await ctx.send('Activity tracking has been enabled')

    @activity.command(name='disable', wants_db=True)
    @dpy_commands.guild_only()
    @checks.can_config()
    async def activity_disable(self, ctx: commands.Context):
        """Disable activity tracking for this server"""

        await ActivityService.set_tracking_state(ctx.db, ctx.guild.id, False)
        self.wants_activity_tracking.remove(ctx.guild.id)

        await ctx.send('Activity tracking has been disabled')

    @tasks.loop(minutes=60)
    async def stats_loop(self):
        if keys.debug:
            return

        session: aiohttp.ClientSession = self.bot.session
        try:
            await session.post(
                f'https://top.gg/api/bots/{self.bot.user.id}/stats',
                json={'server_count': len(self.bot.guilds)},
                headers={'Authorization': keys.dbl_token}
            )

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
        except BaseException as exception:
            tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__, 5))
            return await logger.error(embed=discord.Embed(
                title='An error occurred while posting stats',
                description=tb,
                color=discord.Color.red(),
            ))

        await logger.info("Successfully posted stats")

    @stats_loop.before_loop
    async def before_stats_loop(self):
        await self.bot.wait_until_ready()

    @dpy_commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if guild.id not in self.wants_activity_tracking:
            return

        async with self.bot.db.acquire() as db:
            await ActivityService.delete_for_guild(db, guild.id)

        self.wants_activity_tracking.discard(guild.id)

        await logger.info(f'Deleted activity for guild id {guild.id}')

    @dpy_commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id not in self.wants_activity_tracking:
            return

        async with self.bot.db.acquire() as db:
            await ActivityService.delete_for_member(db, member.guild.id, member.id)

        await logger.debug(f'Deleted activity for member {member.id} in guild id {member.guild.id}')


def setup(bot):
    bot.add_cog(Stats(bot))
