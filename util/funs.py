import asyncio
from random import randint
from typing import Union
import discord
from keys import logWebhook


def random_discord_color():
    return discord.Color(value=randint(0, 16777215))


def format_human_readable_user(user: Union[discord.Member, discord.Member]):
    return f'{user.display_name} ({user.name}#{user.discriminator}, id: {user.id})'


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

    webhook = discord.Webhook.from_url(logWebhook, adapter=discord.AsyncWebhookAdapter(ctx.bot.clientSession))
    await webhook.send(embed=embed, username=ctx.command.name)


async def run_shell_command(command):
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    result = await process.communicate()
    return [out.decode() for out in result]
