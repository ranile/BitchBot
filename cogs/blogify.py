# pylint: disable=function-redefined
from discord.ext import commands
import discord
import requests
import datetime
import urllib
from util.funs import random_discord_color # pylint: disable=no-name-in-module
from keys import blogifyHost


BLOGIFY_API_URL = f'http://{blogifyHost}:8080/api'
BLOGIFY_URL = 'http://172.105.28.10:8080'


class Blogify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def blogify(self, ctx):
        """Commands for blogify
        """
        pass

    @blogify.group(invoke_without_command=True)
    async def articles(self, ctx, uuid = None):
        """Articles group
        """
        if uuid is None:
            articles = requests.get(f'{BLOGIFY_API_URL}/articles?fields=title,summary').json()

            embed = discord.Embed(title="Articles", color = random_discord_color(), url = BLOGIFY_URL)
            embed.set_footer(text = 'From Blogify')

            for article in articles:
                embed.add_field(name=f'**{article["title"]}**', value = article['summary'], inline=False)
            
            await ctx.send(embed=embed)

        else:

            article = requests.get(f'{BLOGIFY_API_URL}/articles/{uuid}?fields=title,content,createdAt,createdBy').json()

            embed = discord.Embed(title=article['title'], color = random_discord_color(), url = f'{BLOGIFY_URL}/article/{uuid}')

            try:
                user = requests.get(f'{BLOGIFY_API_URL}/users/{article["createdBy"]}/?fields=username,profilePicture').json()
                embed.set_author(name=user['username'], url= f'{BLOGIFY_URL}/profile/{user["username"]}', icon_url=f'{BLOGIFY_API_URL}/get/{user["profilePicture"]["fileId"]}')
            except KeyError:
                pass

            embed.timestamp = datetime.datetime.fromtimestamp(int(str(article['createdAt'])[:-3]))
            embed.set_footer(text = 'From Blogify')

            embed.description = article['content'] if len(article['content']) < 2000 else (article['content'][:1988] + '**snippet**')
            
            await ctx.send(embed=embed)

    @articles.command()
    async def search(self, ctx, query):
        """
        """

        articles = requests.get(f'{BLOGIFY_API_URL}/articles/search?q={query}&fields=title,summary').json()
        
        embed = discord.Embed(title="Articles", color = random_discord_color(), url = f'{BLOGIFY_URL}/home;search="{urllib.parse.quote(query)}"')
        embed.set_footer(text = 'From Blogify')

        if articles['found'] is None:
            embed.description = 'No results found :('
            await ctx.send(embed=embed)
            return

        for article in articles["hits"]:
            article = article['document']
            embed.add_field(name=f'**{article["title"]}**', value = article['summary'], inline=False)
        
        await ctx.send(embed=embed)

    @blogify.group(invoke_without_command=False)
    async def users(self, ctx):
        """Users group
        """
        pass

    @users.command()
    async def profile(self, ctx, username):
        """
        """

        user = requests.get(f'{BLOGIFY_API_URL}/users/byUsername/{username}/?fields=username,profilePicture,name').json()

        embed = discord.Embed(color = random_discord_color())
        embed.add_field(name='**Username**', value=user['username'], inline=False)
        embed.add_field(name='**Name**', value=user['name'], inline=False)
        embed.add_field(name='**Profile**', value=f'[Go to profile]({BLOGIFY_URL}/profile/{user["username"]})', inline=False)
        try:
            embed.set_thumbnail(url = f'{BLOGIFY_API_URL}/get/{user["profilePicture"]["fileId"]}')
        except KeyError:
            pass

        embed.set_footer(text = 'From Blogify')
        
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Blogify(bot))
