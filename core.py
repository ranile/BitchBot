import discord
from discord.ext import commands
from keys import bot as BOT_TOKEN

# import os
# BOT_TOKEN = os.environ['BOT_TOKEN']


bot = commands.Bot(command_prefix=">", case_insensitive=True, owner_ids =[529535587728752644])

cogs = ["autorespond", "internet", "poll"] #moderation is not here because it is not working. You can try it out by adding 'moderation' in this list


@bot.event
async def on_ready():
    print(bot.user.name + " is running")
    print("-"*len(bot.user.name + " is running"))
    await bot.change_presence(status=discord.Status('online'), activity=discord.Game("use {}help".format(bot.command_prefix)))
    for i in cogs:
        bot.load_extension("cogs." + i)

bot.run(BOT_TOKEN)
