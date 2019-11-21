import discord, random, re, inspect
from discord.ext import commands
from util import funs
# from keys import bot as BOT_TOKEN

import os
BOT_TOKEN = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix=">", case_insensitive=True,
                   owner_ids=[529535587728752644])

cogs = ["admin", "autorespond", "emojis", "internet", "misc"]

@bot.command()
async def reload(ctx: commands.Context, module: str):
    """
    Reloads a cog

    Args:
        module: The cog to reload
    """

    if (await bot.is_owner(ctx.author)):
        bot.reload_extension(f'cogs.{module}')
        await ctx.send("🔄")

bot.remove_command('help')

def getInfoFromDocstring(docstring):
    """Gets information from docstring formatted using Google's python styleguide.

    Args:
        docstring: The doctring to extract information from.

    Returns:
        Tuple of dict of the aruguments and their docs and everything in the docstring before the word `Args: `.

    """

    splitted = docstring.split("Args:\n")
    args = inspect.cleandoc(splitted[1].split('Returns:\n')[0]).split('\n')

    docs = {}
    for arg in args:
        matched = re.search(r'\w+: ', arg)

        if not matched:
            continue

        argName = matched.group(0)[:-2]
        argDoc = arg[len(argName):][1:].strip()

        docs[argName] = argDoc

    return docs, splitted[0][:-2]

def generateArgStringForEmbed(args):
    out = ''
    keys = list(args.keys())
    values = list(args.values())
    for i in range(len(args)):
        out += f'**{keys[i]}**: {values[i]}\n'
    
    return out

def canRunCommand(ctx, command):
    try:
        canRun = command.can_run(ctx)
    except:
        canRun = False
    
    return canRun

@bot.command()
async def help(ctx: commands.Context, command: str = None):
    """
    Displays help message

    Args:
        command: The command to get help for. Optional
    """

    embed = discord.Embed(title='**You wanted help? Help is provided**', color = funs.random_discord_color())
    
    embed.set_footer(text=f'Do {bot.command_prefix}help commndName to get help for a specific command')

    if command is None:

        for name, cog in bot.cogs.items():
            out = ''
            for cmd in cog.get_commands():
                if not canRunCommand(ctx, cmd):
                    continue

                helpStr = str(cmd.help).split('\n')[0]
                out += f"**{cmd.name}**:\t{helpStr}\n"
                
            if out:
                embed.add_field(name=f'**{name}**', value=out, inline=False)
        
        out = ''
        cmds = [help, reload]
        for cmd in cmds:
            if not canRunCommand(ctx, cmd):
                continue

            helpStr = str(cmd.help).split('\n')[0]
            out += f"**{cmd.name}**:\t{helpStr}\n"

        if out:
            embed.add_field(name='**Uncategorized**', value=out, inline=False)
    else:
        
        cmd = bot.get_command(command)

        if cmd is None:
            await ctx.send(f"Command {command} doesn't exist")
            return

        elif not canRunCommand(ctx, cmd):
            await ctx.send(f"You don't have permission to run {command} command")
            return

        commandHelp = getInfoFromDocstring(cmd.help)
        print(commandHelp[0])
        embed.add_field(name = f'{cmd.name}', value = commandHelp[1], inline=False)

        argsString = generateArgStringForEmbed(commandHelp[0])
        if argsString is not None and argsString != "":
            embed.add_field(name = f'Parameters', value = argsString, inline=False)
        

        cmdAliases = cmd.aliases
        if (cmdAliases):
            aliases = ', '.join(cmdAliases)
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
