import logging
import parsedatetime
from discord.ext import commands

from resources import Timer
import pendulum

logger = logging.getLogger(__name__)


def _parse_time(ctx, time):
    cal = parsedatetime.Calendar()
    now = ctx.message.created_at
    return cal.parseDT(datetimeString=time, sourceTime=now)


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, time, *, text):
        time, _ = _parse_time(ctx, time)

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
        await ctx.send(f"{ctx.author.mention} in {delta}:\n{timer.kwargs['text']}")

    @commands.Cog.listener()
    async def on_reminder_timer_complete(self, timer):
        channel = self.bot.get_channel(timer.kwargs['channel_id'])
        member = self.bot.get_guild(timer.kwargs['guild_id']).get_member(timer.kwargs['author_id'])
        delta = (pendulum.instance(timer.expires_at) - pendulum.now()).in_words()
        await channel.send(f"{member.mention}, {delta} ago: {timer.kwargs['text']}")


def setup(bot):
    bot.add_cog(Reminders(bot))
