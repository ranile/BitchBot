from discord.ext import commands
from keys import can_use_private_commands


def private_command():
    async def predicate(ctx):
        if ctx.author.id not in can_use_private_commands:
            await ctx.send("You can't use this comamnd")
            return False
        else:
            return True

    return commands.check(predicate)
