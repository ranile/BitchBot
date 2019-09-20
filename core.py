import discord
from discord.ext import commands
from keys import bot as BOT_TOKEN

# import os
# BOT_TOKEN = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix=">", case_insensitive=True, owner_ids =[529535587728752644])

# cogs = ["admin", "autorespond", "internet", "poll", 'caseconversion', "stupidity", "games", "math", "tempconversion", "emojis", "servermanagement"]
cogs = ["stupidity", "admin"]

@bot.event
async def on_ready():
    print(f"{bot.user.name} is running")
    print("-"*len(bot.user.name + " is running"))
    await bot.change_presence(status=discord.Status('online'), activity=discord.Game(f"use {bot.command_prefix}help"))
    for i in cogs:
        bot.load_extension(f"cogs.{i}")

bot.run(BOT_TOKEN)
