from discord.ext import commands
import keys
from BitchBot import BitchBot

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'activity', 'jsk', 'logs', 'mod', 'misc']

bot = BitchBot()


@bot.command()
@commands.is_owner()
async def reload(ctx, module):
    """
    Reloads a cog

    Args:
        module: The cog to reload
    """

    bot.reload_extension(f'cogs.{module}')
    await ctx.send("🔄")

bot.run(keys.bot, cogs=cogs)
