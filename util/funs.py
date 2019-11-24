import discord
from discord.ext import commands
from random import randint
import requests
from keys import logWebhook

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

def log(ctx, username, msg, sentMessage, out = None):

    embed = discord.Embed(color = random_discord_color(), description = msg)
    embed.set_author(name= f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
    embed.timestamp = ctx.message.created_at

    if out:
        embed.add_field(name = "Output:", value = out, inline=False)
    
    embed.add_field(name = 'Message', value = f'[Jump To Message]({sentMessage.jump_url})')

    data = {
        "username": username,
        "embeds": [embed.to_dict()]
    }
    requests.post(logWebhook, json=data)
