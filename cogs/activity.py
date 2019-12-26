import datetime
import re

import discord
from discord.ext import commands

from services import ActivityService
from util import funs


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

    def should_increment(self, message):
        try:
            cached = self.cache[f'{message.author.id}-{message.guild.id}']
        except KeyError:
            cached = None

        return (
                (cached is None or
                 (datetime.datetime.now(tz=cached.tzinfo) - cached) > datetime.timedelta(seconds=30)) and
                (not re.match(self.command_pattern, message.content) and
                 not message.author.bot and
                 not re.match(self.bot_channel_pattern, message.channel.name))
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.should_increment(message):
            incremented = await ActivityService.increment(message.author.id, message.guild.id, 5)

            last_updated = (await ActivityService.get(message.author.id, message.guild.id)).last_updated_time
            self.cache[f'{message.author.id}-{message.guild.id}'] = last_updated

            await message.channel.send(f'yes {incremented["points"]}')
        else:
            await message.channel.send('no')

    @commands.group(invoke_without_command=True)
    async def activity(self, ctx):
        fetched = await ActivityService.get(ctx.author.id, ctx.guild.id)
        embed = discord.Embed(color=funs.random_discord_color())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='Activity Points', value=fetched.points)
        embed.add_field(name='Position', value=fetched.position)
        embed.set_footer(text='Last updated at')
        embed.timestamp = fetched.last_updated_time
        await ctx.send(embed=embed)

    @activity.command(name='top')
    async def top_users(self, ctx):
        top = await ActivityService.get_top(guild=ctx.guild)

        paginator = commands.Paginator(prefix='```md')

        length = 0
        for user in top:
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


def setup(bot):
    bot.add_cog(Activity(bot))
