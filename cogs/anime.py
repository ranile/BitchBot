import random

import discord
from discord.ext import commands
from bs4 import BeautifulSoup

from util.checks import private_command


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @private_command()
    async def hug(self, ctx):
        url = 'https://tenor.com/search/anime-hugs-gifs'
        async with self.bot.clientSession.get(url, headers={'content-type': 'text/html'}) as res:
            text = await res.content.read()
            soup = BeautifulSoup(text, 'html.parser')
            imgs = soup.find_all(name='img')
            links = []
            for img in imgs:
                src = str(img.get('src'))
                if src.startswith('http') and src.endswith('gif'):
                    links.append(src)

            await ctx.send(random.choice(links))


def setup(bot):
    bot.add_cog(Anime(bot))
