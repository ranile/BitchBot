import discord
from discord.ext import commands
import parsedatetime


class FetchedUser(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument('Not a valid user ID.')
        try:
            return await ctx.bot.fetch_user(argument)
        except discord.NotFound:
            raise commands.BadArgument('User not found.')
        except discord.HTTPException:
            raise commands.BadArgument('An error occurred while fetching the user.')


class HumanTime(commands.Converter):
    def __init__(self, converter: commands.Converter = None, other=False):
        self.other = other
        self.converter = converter

    class HumanTimeOutput:
        def __init__(self, time, other=None):
            self.time = time
            self.other = other

    def sanitized_time(self, time, now):
        if time.hour == 0 and time.minute == 0:
            time = time.replace(day=time.day + 1)

        if time < now:
            raise commands.BadArgument('Time is in the past')

        return time

    # noinspection DuplicatedCode,PyMethodMayBeStatic
    def get_time(self, user_input):
        words = user_input.split(' ')
        if words[0].isdigit():
            inp = ' '.join(words[:2])
            other = ' '.join(words[2:])
        else:
            inp = words[0]
            other = ' '.join(words[1:])
        return inp, other.strip()

    async def convert(self, ctx, argument):
        cal = parsedatetime.Calendar()

        now = ctx.message.created_at
        actual_time, other_arg = self.get_time(argument)
        dt, _ = cal.parseDT(datetimeString=actual_time, sourceTime=now)
        time = self.sanitized_time(dt, now)
        if self.other and self.converter:
            other_arg = await self.converter.convert(ctx, other_arg)

        return HumanTime.HumanTimeOutput(time, other_arg)
