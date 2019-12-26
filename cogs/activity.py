import datetime

import discord
from discord.ext import commands

from services import ActivityService
from util import funs


class Activity(commands.Cog, name='Activity Tracking'):
    """Tracks your activity in the guild and give them activity points for being active.
    With the end goal being the ability to spend these points on a virtual store
    Currently a WIP
    TODOs (for now):
    • TODO: Implement basic tracking of user's activity
    • TODO: Allow users to see their activity
    • TODO: Allow users to see top users in a guild
    """

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        try:
            cached = self.cache[f'{message.author.id}-{message.guild.id}']
        except KeyError:
            cached = None

        if cached is None or (datetime.datetime.now(tz=cached.tzinfo) - cached) > datetime.timedelta(seconds=5):
            incremented = await ActivityService.increment(message.author.id, message.guild.id, 5)

            last_updated = (await ActivityService.get(message.author.id, message.guild.id))['last_time_updated']
            self.cache[f'{message.author.id}-{message.guild.id}'] = last_updated

            await message.channel.send(f'yes {incremented["points"]}')
        else:
            await message.channel.send('no')

    @commands.group(invoke_without_command=True)
    async def activity(self, ctx):
        fetched = await ActivityService.get(ctx.author.id, ctx.guild.id)
        embed = discord.Embed(color=funs.random_discord_color())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name='Activity Points', value=fetched['points'])
        embed.set_footer(text='Last updated at')
        embed.timestamp = fetched['last_time_updated']
        await ctx.send(embed=embed)

    @activity.command(name='top')
    async def top_users(self, ctx):
        await ctx.send('Stub!')


def setup(bot):
    bot.add_cog(Activity(bot))
