from typing import Union

import discord
from discord.ext import commands
from random import randint

from keys import logWebhook, rabbitWebhook
import inspect
import re


def random_discord_color():
    return discord.Color(value=randint(0, 16777215))


def format_human_readable_user(user: Union[discord.Member, discord.Member]):
    return f'{user.display_name} ({user.name}#{user.discriminator}, id: {user.id})'


def cause_check():
    def predicate(ctx):
        guild = ctx.guild

        if guild.id == 505655510263922700:
            return True
        else:
            return False

    return commands.check(predicate)


def parse_docstring(docstring):
    """Gets information from docstring formatted using Google's python style guide.

    Args:
        docstring: The docstring to extract information from.

    Returns:
        Tuple of dict of the arguments and their docs and everything in the docstring before the word `Args: `.
    """

    split = docstring.split("Args:\n")
    args = inspect.cleandoc(split[1]).split('\n')

    docs = {}
    for arg in args:
        matched = re.search(r'\w+: ', arg)

        if not matched:
            continue

        name = matched.group(0)[:-2]
        doc = arg[len(name):][1:].strip()

        docs[name] = doc

    return docs, split[0][:-2]


# noinspection PyPep8Naming
async def canRunCommand(ctx, command):
    try:
        canRun = await command.can_run(ctx)
    except:
        canRun = False

    return canRun


# noinspection PyPep8Naming
async def log(ctx, msg, sentMessage, out=None):
    embed = discord.Embed(color=random_discord_color(), description=msg)
    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
    embed.timestamp = ctx.message.created_at

    if out:
        embed.add_field(name="Output:", value=out, inline=False)

    embed.add_field(name='Message', value=f'[Jump To Message]({sentMessage.jump_url})')

    webhook = discord.Webhook.from_url(logWebhook, adapter=discord.AsyncWebhookAdapter(ctx.bot.clientSession))
    await webhook.send(embed=embed, username=ctx.command.name)


# noinspection PyPep8Naming
async def sendRabbitCounterUpdate(bot, msg):
    pfp = 'https://raw.githubusercontent.com/hamza1311/BitchBot/master/res/rabbitman2.jpg'

    webhook = discord.Webhook.from_url(rabbitWebhook, adapter=discord.AsyncWebhookAdapter(bot.clientSession))
    await webhook.send(msg, username='Rabbit', avatar_url=pfp)

