import asyncio
import functools
from random import randint
from typing import Union
import discord
from quart import session
from requests_oauthlib import OAuth2Session

import keys
from .consts import *


def random_discord_color():
    return discord.Color(value=randint(0, 16777215))


def format_human_readable_user(user: Union[discord.Member, discord.Member]):
    if user is discord.Member:
        return f'{user.display_name} ({user.name}#{user.discriminator}, id: {user.id})'
    else:
        return str(user)


# noinspection PyPep8Naming
async def canRunCommand(ctx, command):
    try:
        canRun = await command.can_run(ctx)
    except:
        canRun = False

    return canRun


async def log(ctx, msg, sent_message, out=None):
    embed = discord.Embed(color=random_discord_color(), description=msg)
    embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
    embed.timestamp = ctx.message.created_at

    if out:
        embed.add_field(name="Output:", value=out, inline=False)

    embed.add_field(name='Message', value=f'[Jump To Message]({sent_message.jump_url})')

    webhook = discord.Webhook.from_url(keys.logWebhook, adapter=discord.AsyncWebhookAdapter(ctx.bot.clientSession))
    await webhook.send(embed=embed, username=ctx.command.name)


async def run_shell_command(command):
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    result = await process.communicate()
    return [out.decode() for out in result]


async def run_in_executor(partial_func):
    return await asyncio.get_event_loop().run_in_executor(None, partial_func)


async def fetch_user_from_session(_session):
    user = (await run_in_executor(functools.partial(_session.get, 'https://discordapp.com/api/users/@me')))
    print('hitting discord')
    return user


def token_updater(token):
    session['oauth2_token'] = token


def make_oauth_session(token=None, state=None, scopes=None):
    return OAuth2Session(
        client_id=keys.client_id,
        token=token,
        state=state,
        scope=scopes,
        redirect_uri=keys.redirect_uri,
        auto_refresh_kwargs={
            'client_id': keys.client_id,
            'client_secret': keys.redirect_uri,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater,
    )


def space(count=4):
    return f'{ZWS} ' * count
