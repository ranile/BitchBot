import discord, random
from discord.ext import commands
# from keys import bot as BOT_TOKEN

import os
BOT_TOKEN = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix=">", case_insensitive=True,
                   owner_ids=[529535587728752644])

# cogs = ["admin", "autorespond", "emojis", "games", "internet", "poll", "stupidity", "servermanagement"]
cogs = ["admin", "autorespond", "emojis", "internet", "poll", "misc", "quotes-and-counters"]

@bot.command()
async def reload(ctx: commands.Context, module: str):
    """
    Reloads a cog
    """

    if (await bot.is_owner(ctx.author)):
        bot.reload_extension(f'cogs.{module}')
        await ctx.send("🔄")

bot.remove_command('help')

@bot.command()
async def help(ctx: commands.Context, command: str = None):
    """
    Displays help message
    """

    embed = discord.Embed(title='**You wanted help? Help is provided**')
    embed.colour = discord.Color(value=random.randint(0, 16777215))
    embed.set_footer(text=f'Do {bot.command_prefix}help commndName to get help for a specific command')

    if command is None:

        for name, cog in bot.cogs.items():
            out = ''
            for cmd in cog.get_commands():

                helpStr = str(cmd.help).split('\n')[0]
                out += f"**{cmd.name}**:\t{helpStr}\n"

            embed.add_field(name=f'**{name}**', value=out, inline=False)
        
        out = ''
        cmds = [help, reload]
        for cmd in cmds:
            helpStr = str(cmd.help).split('\n')[0]
            out += f"**{cmd.name}**:\t{helpStr}\n"

        embed.add_field(name='**Uncategorized**', value=out, inline=False)
    else:
        
        cmd = bot.get_command(command)

        if cmd is None:
            await ctx.send(f"Command {command} doesn't exist")

        embed.add_field(name = f'{cmd.name}', value = cmd.help, inline=False)

        cmdAliases = cmd.aliases
        if (cmdAliases):
            aliases = ''
            for i in range(0, len(cmdAliases)):
                aliases += f'{i + 1}. {cmdAliases[i]}\n'

            embed.add_field(name='Aliases:', value=aliases, inline=False)
        
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is running")
    print("-"*len(bot.user.name + " is running"))
    await bot.change_presence(
        status=discord.Status('online'),
        activity=discord.Game(f"use {bot.command_prefix}help")
    )

    for i in cogs:
        bot.load_extension(f"cogs.{i}")

bot.run(BOT_TOKEN)
