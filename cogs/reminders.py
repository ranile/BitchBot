import discord
from discord.ext import commands as dpy_commands
import textwrap

import util
from BitchBot import BitchBot
from resources import Timer
import pendulum

from services import TimersService
from util import HumanTime, commands


class Reminders(dpy_commands.Cog):
    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot

    # noinspection PyIncorrectDocstring,PyUnresolvedReferences
    @commands.group(invoke_without_command=True, usage='<time> <text>')
    async def remind(self, ctx: commands.Context, *, time_and_text: HumanTime(other=True)):
        """
        Reminds you of something after a certain amount of time.

        Args:
            time: When you want to be reminded; should be a relative time like 2h, 1d, etc
            text: What you want to be reminded of
        """

        time, text = time_and_text.time, time_and_text.other

        timer = Timer(
            event='reminder',
            created_at=ctx.message.created_at,
            expires_at=time,
            kwargs={
                'author_id': ctx.author.id,
                'guild_id': ctx.guild.id,
                'channel_id': ctx.channel.id,
                'text': text
            }
        )
        await self.bot.timers.create_timer(timer)
        delta = (pendulum.instance(timer.expires_at) - pendulum.instance(ctx.message.created_at)).in_words()
        await ctx.send(f"{ctx.author.display_name} in {delta}:\n{timer.kwargs['text']}")

    @remind.command(name='list', aliases=['get'], wants_db=True)
    async def reminders_list(self, ctx: commands.Context):
        """
        Show 10 of your upcoming reminders
        """

        fetched = await TimersService.get_where(ctx.db, extras={"author_id": ctx.author.id}, limit=10)
        if len(fetched) == 0:
            return await ctx.send('No currently running reminders')

        embed = discord.Embed(
            title='Upcoming reminders',
            color=util.random_discord_color()
        )
        embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))

        for timer in fetched:
            text = f"{textwrap.shorten(timer.kwargs['text'], width=512)}"
            embed.add_field(
                name=f'ID: {timer.id}, in {(pendulum.instance(timer.expires_at) - pendulum.now()).in_words()}',
                value=text, inline=False
            )

        await ctx.send(embed=embed)

    @dpy_commands.Cog.listener()
    async def on_reminder_timer_complete(self, timer: Timer):
        channel = self.bot.get_channel(timer.kwargs['channel_id'])
        member = self.bot.get_guild(timer.kwargs['guild_id']).get_member(timer.kwargs['author_id'])
        delta = (pendulum.instance(timer.expires_at) - pendulum.instance(timer.created_at)).in_words()
        await channel.send(f"{member.mention}, {delta} ago:\n{timer.kwargs['text']}")


def setup(bot):
    bot.add_cog(Reminders(bot))
