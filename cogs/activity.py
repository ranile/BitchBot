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
    """Tracks your activity in the guild and give them activity points for being active."""

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.bot_channel_pattern = re.compile(r'(bot-?commands|spam)')
        self.command_pattern = re.compile(rf'>[a-z]+')
        self.activity_service = ActivityService(self.bot.db)

    def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("Activity Tracking not available in DMs")
        return True

    @commands.group(invoke_without_command=True)
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
            embed = discord.Embed(color=funs.random_discord_color())
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)
            embed.add_field(name='Activity Points', value=fetched.points)
            embed.add_field(name='Position', value=fetched.position)
            embed.set_footer(text='Last updated at')
            embed.timestamp = fetched.last_updated_time
            await ctx.send(embed=embed)
        except errors.NotFound:
            await ctx.send(f'Activity for user `{funs.format_human_readable_user(target)}` not found')

    @activity.command(name='top')
    async def top_users(self, ctx, amount=10):
        """Shows top users in server's activity leaderboard"""
        top = await self.activity_service.get_top(guild=ctx.guild, limit=amount)

        paginator = commands.Paginator(prefix='```md')

        length = 0
        count = 0
        for user in top:
            member = ctx.guild.get_member(user.user_id)
            line = f'{count + 1}. {member.display_name} - {user.points} points'
            paginator.add_line(line)
            if length < len(line):
                length = len(line)
            count += 1

        paginator.add_line()
        paginator.add_line('-' * length)
        me = await self.activity_service.get(ctx.author)
        paginator.add_line(f'You have {me.points} points')

        for page in paginator.pages:
            await ctx.send(page)


def setup(bot):
    bot.add_cog(Activity(bot))
