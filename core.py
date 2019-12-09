import asyncio

import discord
import tornado.web
from discord.ext import commands

from database import database
from keys import bot as BOT_TOKEN
from routes.routes import routesList as routes
from services.article_service import ArticleService
from util import HelpCommand, funs
import aiohttp

bot = commands.Bot(
    command_prefix=">",
    case_insensitive=True,
    owner_ids=[529535587728752644],
    help_command=HelpCommand.BloodyHelpCommand()
)

# cogs = ["admin", "autorespond", "emojis", "internet", "misc", "blogify"]
cogs = ["admin", "internet", "misc", "blogify"]

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

    # async with bot.aiohttpClientSession as cs:
    #     async with cs.get(f'{functionsUrl}/config') as r:
    #         bot.config = await r.json()

    for i in cogs:
        bot.load_extension(f"cogs.{i}")

    articles = await ArticleService().get()
    for a in articles:
        print(a)


app = tornado.web.Application([(route, handler, dict(bot=bot)) for route, handler in routes], **{
    'debug': True
})
app.listen(6969)
loop = asyncio.get_event_loop()
# loop.create_task(funs.motivate())
asyncio.ensure_future(database.init(), loop=loop)
# asyncio.ensure_future(bot.start(BOT_TOKEN), loop=loop)
loop.run_forever()
