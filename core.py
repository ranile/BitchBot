import asyncio

# noinspection PyPackageRequirements
import discord
import tornado.web
# noinspection PyPackageRequirements
from discord.ext import commands

from database import database
from keys import bot as BOT_TOKEN
from routes.routes import routesList as routes
from util import HelpCommand
# noinspection PyPackageRequirements
import aiohttp
import logging

bot = commands.Bot(
    command_prefix=">",
    case_insensitive=True,
    owner_id=529535587728752644,
    help_command=HelpCommand.BloodyHelpCommand()
)

dpy_logger = logging.getLogger('discord')
dpy_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s: %(asctime)s: %(message)s'))
dpy_logger.addHandler(handler)

cogs = ["admin", "cause", "emojis", "internet", "starboard", 'activity', 'jsk', 'logs', 'mod', 'misc', 'anime']


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
    print("-" * len(bot.user.name + " is running"))
    await bot.change_presence(
        status=discord.Status('online'),
        activity=discord.Game(f"use {bot.command_prefix}help")
    )

    bot.clientSession = aiohttp.ClientSession()
    for i in cogs:
        bot.load_extension(f"cogs.{i}")


async def close():
    await bot.logout()


async def start():
    try:
        pool = await database.init(loop)
        bot.db = pool
        await bot.start(BOT_TOKEN)
    finally:
        await bot.close()


def stop_loop_on_completion(_):
    loop.stop()


app = tornado.web.Application([(route, handler, dict(bot=bot)) for route, handler in routes], **{
    'debug': True
})
# app.listen(6969)
loop = asyncio.get_event_loop()

future = asyncio.ensure_future(start(), loop=loop)
future.add_done_callback(stop_loop_on_completion)
try:
    loop.run_forever()
finally:
    future.remove_done_callback(stop_loop_on_completion)
