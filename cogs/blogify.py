# pylint: disable=function-redefined
from discord.ext import commands
import discord
import requests
import datetime
from util.funs import random_discord_color # pylint: disable=no-name-in-module


BLOGIFY_API_URL = 'http://172.105.28.10:8080/api'
BLOGIFY_URL = 'http://172.105.28.10:8080'


class Blogify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blogify(self, ctx):
        """Commands for blogify
        """

        pass
    
    @blogify.group(invoke_without_command=False)
    async def users(self, ctx):
        """Users group
        """

        await ctx.send('users')

    @blogify.group(invoke_without_command=True)
    async def articles(self, ctx):
        """Articles group
        """

        articles = requests.get(f'{BLOGIFY_API_URL}/articles?fields=title,summary').json()

        embed = discord.Embed(title="Articles", color = random_discord_color(), url = BLOGIFY_URL)
        embed.set_footer(text = 'From Blogify')

        for article in articles:
            embed.add_field(name=f'**{article["title"]}**', value = article['summary'], inline=False)
        
        await ctx.send(embed=embed)
    
    @articles.group()
    async def uuid(self, ctx, uuid):
        """
        """

        article = requests.get(f'{BLOGIFY_API_URL}/articles/{uuid}?fields=title,content,createdAt,createdBy').json()

        embed = discord.Embed(title=article['title'], color = random_discord_color(), url = f'{BLOGIFY_URL}/article/{uuid}')

        user = requests.get(f'{BLOGIFY_API_URL}/users/{article["createdBy"]}/?fields=username,profilePicture').json()
        embed.set_author(name=user['username'], url= f'{BLOGIFY_URL}/profile/{user["username"]}', icon_url=f'{BLOGIFY_API_URL}/get/{user["profilePicture"]["fileId"]}')
        
        embed.timestamp = datetime.datetime.fromtimestamp(int(str(article['createdAt'])[:-3]))
        embed.set_footer(text = 'From Blogify')

        embed.description = article['content'] if len(article['content']) < 2000 else (article['content'][:1988] + '**snippet**')
        
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Blogify(bot))
