from discord.ext import commands
import keys
from services import ConfigService


def private_command():
    async def predicate(ctx):
        if ctx.author.id not in keys.can_use_private_commands:
            raise commands.CheckFailure("You can't use this command")
        else:
            return True

    return commands.check(predicate)


def can_config():
    async def predicate(ctx):
        if ctx.author.id == ctx.bot.owner_id or ctx.channel.permissions_for(ctx.author).manage_guild:
            return True
        else:
            raise commands.CheckFailure("You need Manage Server permissions to run this command")

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


def owner_only_in_non_trusted_guilds():
    async def predicate(ctx):
        is_owner = await ctx.bot.is_owner(ctx.author)
        if ctx.guild.id in keys.trusted_guilds or is_owner:
            return True
        else:
            raise commands.CheckFailure("You can't use this command")

    return commands.check(predicate)


def nsfw_only_in_non_trusted_guilds():
    async def predicate(ctx):
        is_owner = await ctx.bot.is_owner(ctx.author)
        if ctx.guild is None or is_owner:
            return True
        elif ctx.guild.id in keys.trusted_guilds or ctx.channel.is_nsfw():
            return True
        else:
            # thanks bot lists
            raise commands.CheckFailure(f"This command can only be used in an NSFW channel or DMs with the bot")

    return commands.check(predicate)
