from discord.ext import commands
import dateparser
import functools


class HumanTime(commands.Converter):
    def __init__(self, converter: commands.Converter = None, other=False):
        self.other = other
        self.other_converter = converter

    class HumanTimeOutput:
        def __init__(self, time, other=None):
            self.time = time
            self.other = other

    def parse(self, user_input, ctx):
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
        for i in range(length, 0, -1):
            used = " ".join(split[:i])
            out = dateparser.parse(used, settings=settings)
            if out is not None:
                break

        if out is None:
            raise commands.BadArgument('Provided time is invalid')

        now = ctx.message.created_at
        return out.replace(tzinfo=now.tzinfo), ''.join(to_be_passed).replace(used, '')

    def time_check(self, time, ctx):
        now = ctx.message.created_at
        if time is None:
            raise commands.BadArgument('Provided time is invalid')
        elif time < now:
            raise commands.BadArgument('Time is in past')

    async def convert(self, ctx, argument):
        time, other = await ctx.bot.loop.run_in_executor(None, functools.partial(self.parse, argument, ctx))
        self.time_check(time, ctx)
        if self.other_converter is not None:
            other = await self.other_converter.convert(ctx, argument)
        return HumanTime.HumanTimeOutput(time, other)
