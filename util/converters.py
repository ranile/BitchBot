import discord
from discord.ext import commands
from datetime import datetime
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
    async def convert(self, ctx, argument):
        cal = parsedatetime.Calendar()

        now = ctx.message.created_at
        dt, _ = cal.parseDT(datetimeString=argument, sourceTime=now)
        # TODO: Check if `dt` is valid
        return dt
