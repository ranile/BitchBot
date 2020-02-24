import datetime

import discord
from discord.ext import commands
import asyncio
import dateparser
import functools


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


# noinspection PyMethodMayBeStatic
class HumanTime(commands.Converter):
    def __init__(self, converter: commands.Converter = None, other=False):
        self.other = other
        self.other_converter = converter

    class HumanTimeOutput:
        def __init__(self, time, other=None):
            self.time = time
            self.other = other

    def parse(self, user_input):
        settings = {
            'TIMEZONE': 'UTC',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'TO_TIMEZONE': 'UTC',
            'PREFER_DATES_FROM': 'future'
        }

        to_be_passed = f"in {user_input}"
        split = to_be_passed.split(" ")
        length = len(split[:7])
        out = None
        used = ""
        while out is None:
            used = " ".join(split[:length])
            out = dateparser.parse(used, settings=settings)
            length -= 1

        now = datetime.datetime.utcnow()
        return out.replace(tzinfo=now.tzinfo), ''.join(to_be_passed).replace(used, '')

    def time_check(self, time, ctx):
        now = ctx.message.created_at
        if time is None:
            raise commands.BadArgument('Invalid time provided')
        elif time < now:
            raise commands.BadArgument('Time is in past')

    async def convert(self, ctx, argument):
        time, other = await ctx.bot.loop.run_in_executor(None, functools.partial(self.parse, argument))
        self.time_check(time, ctx)
        if self.other_converter is not None:
            other = await self.other_converter.convert(ctx, argument)
        return HumanTime.HumanTimeOutput(time, other)
