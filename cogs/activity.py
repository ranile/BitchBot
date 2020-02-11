import re
import discord
from discord.ext import commands
from services import ActivityService
import util
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


def setup(bot):
    bot.add_cog(Activity(bot))
