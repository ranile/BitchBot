import datetime
import re

import discord
from discord.ext import commands, tasks

from services import ActivityService
from util import funs
from database import errors
import logging

log = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s: %(asctime)s: %(message)s'))
log.addHandler(handler)


class Activity(commands.Cog, name='Activity Tracking'):
    """Tracks your activity in the guild and give them activity points for being active.
    With the end goal being the ability to spend these points on a virtual store
    Currently a WIP
    """

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.bot_channel_pattern = re.compile(r'(bot-?commands|spam)')
        self.command_pattern = re.compile(rf'>[a-z]+')
        log.critical('activity')
        self.refresh_activity_material_view.start()

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
            await ActivityService.increment(message.author.id, message.guild.id, 2)
            try:
                last_updated = (await ActivityService.get(message.author.id, message.guild.id)).last_updated_time
            except errors.NotFound:
                last_updated = datetime.datetime.utcnow()
            self.cache[f'{message.author.id}-{message.guild.id}'] = last_updated

    @commands.group(invoke_without_command=True)
    async def activity(self, ctx, of: discord.Member = None):
        if of is None:
            of = ctx.author
        try:
            fetched = await ActivityService.get(of.id, ctx.guild.id)
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
        top = await ActivityService.get_top(guild=ctx.guild)

        paginator = commands.Paginator(prefix='```md')

        length = 0
        for user in top:
            if user.user is None:
                continue

            line = f'{user.position}. {user.user.display_name} - {user.points} points'
            paginator.add_line(line)
            if length < len(line):
                length = len(line)

        paginator.add_line()
        paginator.add_line('-' * length)
        me = await ActivityService.get(ctx.author.id, ctx.guild.id)
        paginator.add_line(f'{me.position}. You - {me.points}')

        for page in paginator.pages:
            await ctx.send(page)

    @tasks.loop(minutes=30)
    async def refresh_activity_material_view(self):
        await ActivityService.update_material_view()

    @refresh_activity_material_view.before_loop
    async def before_refresh_material_view(self):
        await self.bot.wait_until_ready()

    @refresh_activity_material_view.after_loop
    async def after_refresh_material_view(self):
        log.info('Refreshed ActivityView Material view')


def setup(bot):
    bot.add_cog(Activity(bot))
