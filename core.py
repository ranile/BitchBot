import discord, random, re, inspect
from discord.ext import commands
from keys import bot as BOT_TOKEN, functionsUrl
from util import HelpCommand, funs
import aiohttp

bot = commands.Bot(command_prefix=">", case_insensitive=True,
                   owner_ids=[529535587728752644])

cogs = ["admin", "autorespond", "emojis", "internet", "misc", "blogify"]

bot.help_command = HelpCommand.PaginatedHelpCommand()

@bot.command()
@commands.is_owner()
async def reload(ctx: commands.Context, module: str):
    """
    Reloads a cog

    Args:
        module: The cog to reload
    """

    bot.reload_extension(f'cogs.{module}')
    await ctx.send("🔄")

@bot.event
async def on_ready():
    print(f"{bot.user.name} is running")
    print("-"*len(bot.user.name + " is running"))
    await bot.change_presence(
        status=discord.Status('online'),
        activity=discord.Game(f"use {bot.command_prefix}help")
    )

    bot.aiohttpClientSession = aiohttp.ClientSession()

    async with bot.aiohttpClientSession as cs:
        async with cs.get(f'{functionsUrl}/config') as r:
            bot.config = await r.json()

    for i in cogs:
        bot.load_extension(f"cogs.{i}")

bot.loop.create_task(funs.motivate())

bot.run(BOT_TOKEN)
