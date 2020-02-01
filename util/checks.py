from discord.ext import commands
from keys import can_use_private_commands
from services import ConfigService


def private_command():
    async def predicate(ctx):
        if ctx.author.id not in can_use_private_commands:
            await ctx.send("You can't use this comamnd")
            return False
        else:
            return True

    return commands.check(predicate)


def can_config():
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id or ctx.channel.permissions_for(ctx.author).manage_guild:
            return True
        else:
            return False

    return commands.check(predicate)


def is_mod():
    async def predicate(ctx):
        config = await ConfigService(ctx.bot.db).get(ctx.guild.id)
        if config is None:
            return False
        if set(x.id for x in ctx.author.roles) & set(config.mod_roles):
            return True
        else:
            return False

    return commands.check(predicate)
