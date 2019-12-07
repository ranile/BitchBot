import discord
from discord.ext import commands
from random import randint
import requests
from keys import logWebhook, rabbitWebhook, moritvatorWebhook
import aiohttp
import inspect
import re
import asyncio
import datetime

def random_discord_color():
    return discord.Color(value=randint(0, 16777215))

def cause_check():
    def predicate(ctx):
        if isinstance(ctx, discord.Guild):
            guild = ctx
        else:
            guild = ctx.guild


        if guild.id == 505655510263922700:
            return True
        else:
            return False
        
    return commands.check(predicate)

def getInfoFromDocstring(docstring):
    """Gets information from docstring formatted using Google's python styleguide.

    Args:
        docstring: The doctring to extract information from.

    Returns:
        Tuple of dict of the aruguments and their docs and everything in the docstring before the word `Args: `.

    """

    splitted = docstring.split("Args:\n")
    args = inspect.cleandoc(splitted[1]).split('\n')

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

async def canRunCommand(ctx, command):
    try:
        canRun = await command.can_run(ctx)
    except:
        canRun = False
    
    return canRun

async def log(ctx, username, msg, sentMessage, out = None):

    embed = discord.Embed(color = random_discord_color(), description = msg)
    embed.set_author(name= f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
    embed.timestamp = ctx.message.created_at

    if out:
        embed.add_field(name = "Output:", value = out, inline=False)
    
    embed.add_field(name = 'Message', value = f'[Jump To Message]({sentMessage.jump_url})')

    
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(logWebhook, adapter=discord.AsyncWebhookAdapter(session))
        await webhook.send(embed=embed, username=username)

async def sendRabbitCounterUpdate(msg):
    pfp = 'https://raw.githubusercontent.com/hamza1311/BitchBot/master/res/rabbitman2.jpg'

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(rabbitWebhook, adapter=discord.AsyncWebhookAdapter(session))
        await webhook.send(msg, username='Rabbit', avatar_url=pfp)

async def motivate():
    while True:
        print('called')
        timeTillFreedom = datetime.datetime(year=2019,month=12, day=20, hour=12) - datetime.datetime.now()

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(moritvatorWebhook, adapter=discord.AsyncWebhookAdapter(session))        
            await webhook.send(f'Hey <@529535587728752644>, you got {timeTillFreedom.days} days till freedom.\nPull through!!')
            await asyncio.sleep((24 - (datetime.datetime.utcnow().hour + 5)) * 60 * 60)
            await webhook.send(f'Hey <@529535587728752644>, you got {timeTillFreedom.days} days till freedom.\nPull through!!')
