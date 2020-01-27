import datetime
import re

import discord
from discord.ext import commands, tasks

from services import ActivityService
from util import funs
from database import errors
import logging

log = logging.getLogger(__name__)


class Activity(commands.Cog, name='Activity Tracking'):
    """Tracks your activity in the guild and give them activity points for being active.
    With the end goal being the ability to spend these points on a virtual store
    """

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.bot_channel_pattern = re.compile(r'(bot-?commands|spam)')
        self.command_pattern = re.compile(rf'>[a-z]+')
        self.refresh_activity_material_view.start()
        self.activity_service = ActivityService(self.bot.db)

    def should_increment(self, message):
        try:
            cached = self.cache[f'{message.author.id}-{message.guild.id}']
        except KeyError:
            cached = None

        return (
                (cached is None or
                 (datetime.datetime.now(tz=cached.tzinfo) - cached) > datetime.timedelta(minutes=2)) and
                (not re.match(self.command_pattern, message.content) and
                 not message.author.bot and
                 not re.match(self.bot_channel_pattern, message.channel.name))
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.should_increment(message):
            await self.activity_service.increment(message.author.id, message.guild.id, 2)
            try:
                last_updated = (await self.activity_service.get(message.author.id, message.guild.id)).last_updated_time
            except errors.NotFound:
                last_updated = datetime.datetime.utcnow()
            self.cache[f'{message.author.id}-{message.guild.id}'] = last_updated

    @commands.group(invoke_without_command=True)
    async def activity(self, ctx, of: discord.Member = None):
        """
        Shows activity on the server's leaderboard

         Args:
            of: The member whose activity you want to see. Author's activity is shown if omitted
        """
        if of is None:
            of = ctx.author
        try:
            fetched = await self.activity_service.get(of.id, ctx.guild.id)
            member = ctx.guild.get_member(fetched.user)
            embed = discord.Embed(color=funs.random_discord_color())
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)
            embed.add_field(name='Activity Points', value=fetched.points)
            embed.add_field(name='Position', value=fetched.position)
            embed.set_footer(text='Last updated at')
            embed.timestamp = fetched.last_updated_time
            await ctx.send(embed=embed)
        except errors.NotFound:
            await ctx.send(f'Activity for user `{funs.format_human_readable_user(of)}` not found')

    @activity.command(name='top')
    async def top_users(self, ctx):
        """Shows top users in server's activity leaderboard"""
        top = await self.activity_service.get_top(guild=ctx.guild)

        paginator = commands.Paginator(prefix='```md')

        length = 0
        count = 0
        for user in top:
            if count > 10:
                break
            if user.user is None:
                continue

            line = f'{user.position}. {user.user.display_name} - {user.points} points'
            paginator.add_line(line)
            if length < len(line):
                length = len(line)
            count += 1

        paginator.add_line()
        paginator.add_line('-' * length)
        me = await self.activity_service.get(ctx.author.id, ctx.guild.id)
        paginator.add_line(f'{me.position}. You - {me.points}')

        for page in paginator.pages:
            await ctx.send(page)

    @tasks.loop(minutes=30)
    async def refresh_activity_material_view(self):
        await self.activity_service.update_material_view()

    @refresh_activity_material_view.before_loop
    async def before_refresh_material_view(self):
        log.info('Starting ActivityView Materialized view refresh')

    @refresh_activity_material_view.after_loop
    async def after_refresh_material_view(self):
        log.info('Refreshed ActivityView Materialized view')


def setup(bot):
    bot.add_cog(Activity(bot))
