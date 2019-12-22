import discord
import re
import urllib
import wikipedia
from discord.ext import commands

from util.funs import random_discord_color  # pylint: disable=no-name-in-module
from util.paginator import Paginator


class Internet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_image_regex = re.compile(r".*\.(jpg|png|gif)$")

    @commands.command(aliases=["wiki"])
    async def wikipedia(self, ctx, *, search):
        """
        Find a Wikipedia page on a given topic
        """

        await ctx.channel.trigger_typing()
        search = wikipedia.search(search)

        if not search:
            await ctx.send("No page was found for that search term")
            return

        page = wikipedia.page(search[0])
        title = page.title
        body = page.summary[:1000]
        image = page.images[0]
        url = page.url

        embed = discord.Embed(title=title, description=body, url=url, color=random_discord_color())
        embed.set_footer(text="From Wikipedia")
        embed.set_thumbnail(url=image)

        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        """
        They are horrible. Seriously
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get("https://icanhazdadjoke.com", headers={"Accept": "text/plain"}) as res:
            content = await res.json(content_type=None)

            await ctx.send(content)

    @commands.command()
    async def norris(self, ctx):
        """
        Chuck Norris. Need I say more
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get("https://api.chucknorris.io/jokes/random") as res:
            data = (await res.json())["value"]
            await ctx.send(data)

    @commands.command()
    async def reddit(self, ctx, *, search):
        """
        Get a random reddit post
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get(f'http://reddit.com/r/{search}/new/.json', headers={'User-agent': 'Chrome'}) as res:
            json = await res.json()

            if "error" in json or json["data"]["after"] is None:
                await ctx.send(f"Subreddit '{search}' not found")
                return

            posts = json["data"]["children"]
            embeds = []
            for post in posts:
                post = post['data']

                if post['over_18'] and not ctx.channel.is_nsfw():
                    continue

                embed = discord.Embed(title=post["title"], url=f'https://reddit.com{post["permalink"]}',
                                      color=random_discord_color())
                embed.set_author(name=f'u/{post["author"]}')
                embed.set_footer(text=post['subreddit_name_prefixed'])

                if post['is_self']:
                    embed.description = post['selftext'][:800]
                elif re.match(self.is_image_regex, post['url']):
                    embed.set_image(url=post['url'])

                embeds.append(embed)

        await Paginator(ctx, embeds).paginate()

    @commands.command()
    async def fact(self, ctx):
        """
        Fun fact. U gey
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get("http://randomuselessfact.appspot.com/random.json?language=en") as res:
            await ctx.send(((await res.json())['text']))

    @commands.command(aliases=["belikebill"])
    async def bill(self, ctx, *, name="Bill"):
        """
        Be like bill
        """

        link = f"https://belikebill.ga/billgen-API.php?default=1&name={urllib.parse.quote(name)}"
        await ctx.send(embed=discord.Embed().set_image(url=link))

    @commands.command()
    async def urban(self, ctx, *, query):
        """
        Gets top definition from urban dictionary
        """

        await ctx.channel.trigger_typing()
        search = urllib.parse.quote(query)
        link = f"https://www.urbandictionary.com/define.php?term={search}"

        async with self.bot.clientSession.get(f"http://api.urbandictionary.com/v0/define?term={search}") as res:
            if res.status == 404:
                await ctx.send('Errorrrrr... Not found')
                return
            data = (await res.json())['list']
            embeds = []
            for item in data:
                embed = discord.Embed(title=item['word'], description=item['definition'], url=link,
                                      color=random_discord_color())

                embed.add_field(name="Example", value=item["example"], inline=False)
                embed.set_footer(text="From Urban Dictionary")

                embeds.append(embed)

            await Paginator(ctx, embeds).paginate()

    @commands.command(aliases=["insult"])
    async def roastme(self, ctx):
        """
        Get roasted
        """

        await ctx.channel.trigger_typing()

        async with self.bot.clientSession.get("https://insult.mattbas.org/api/insult.json") as res:
            if res.status != 200:
                await ctx.send("You lucky bastard... An error occurred."
                               "Mission failed bois, we'll get 'em next time")
                return

            await ctx.send((await res.json())['insult'])


def setup(bot):
    bot.add_cog(Internet(bot))
