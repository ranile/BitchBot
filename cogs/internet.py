import discord
import re
from urllib.parse import quote
from discord.ext import commands

from util.funs import random_discord_color
from util import BloodyMenuPages, EmbedPagesData, checks


# noinspection PyIncorrectDocstring
class Internet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_image_regex = re.compile(r".*\.(jpg|png|gif)$")

    @commands.command()
    async def joke(self, ctx):
        """
        They are horrible. Seriously
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get("https://icanhazdadjoke.com",
                                              headers={"Accept": "application/json"}) as res:
            content = await res.json()
            await ctx.send(content['joke'])

    @commands.command()
    async def reddit(self, ctx, *, search):
        """
        Get a random reddit post

        Args:
            search: The subreddit from which you will get the post
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get(f'http://reddit.com/r/{search}/new/.json',
                                              headers={'User-agent': 'Chrome'}) as res:
            json = await res.json()

            if "error" in json or json["data"]["after"] is None:
                await ctx.send(f"Subreddit '{search}' not found")
                return

            posts = json["data"]["children"]
            total_posts = len(posts)
            embeds = []
            over_18 = 0
            for post in posts:
                post = post['data']

                if post['over_18'] and not ctx.channel.is_nsfw():
                    over_18 += 1

                embed = discord.Embed(title=post["title"], url=f'https://reddit.com{post["permalink"]}',
                                      color=random_discord_color())
                embed.set_author(name=f'u/{post["author"]}')
                embed.set_footer(text=post['subreddit_name_prefixed'])

                if post['is_self']:
                    text = post['selftext']
                    embed.description = text[:800] if len(text) < 800 else f'{text[:800]} **--Snippet--**'
                elif re.match(self.is_image_regex, post['url']):
                    embed.set_image(url=post['url'])

                embeds.append(embed)

            if over_18 == total_posts:
                return await ctx.send('All posts found were NSFW. Try in an NSFW channel')
        await BloodyMenuPages(EmbedPagesData(embeds)).start(ctx)

    @commands.command()
    async def fact(self, ctx):
        """
        Fun fact. U gey
        """

        await ctx.channel.trigger_typing()
        async with self.bot.clientSession.get("https://useless-facts.sameerkumar.website/api") as res:
            await ctx.send(((await res.json())['data']))

    @commands.command(aliases=["belikebill"])
    async def bill(self, ctx, *, name="Bill"):
        """
        Be like bill
        """

        link = f"https://belikebill.ga/billgen-API.php?default=1&name={quote(name)}"
        await ctx.send(embed=discord.Embed().set_image(url=link))

    URBAN_LINK_EXP = re.compile(r'(\[(.+?)\])')

    @commands.command()
    @checks.nsfw_only_in_non_trusted_guilds()
    async def urban(self, ctx, *, query):
        """
        Gets top definition from urban dictionary
        
        Args:
            query: A word you want to get defined
        """

        await ctx.channel.trigger_typing()
        search = quote(query)
        link = f"https://www.urbandictionary.com/define.php?term={search}"

        async with self.bot.clientSession.get(f"http://api.urbandictionary.com/v0/define",
                                              params={'term': query}) as res:
            if res.status != 200:
                await ctx.send(f'Errorrrrr... {res.status}: {res.reason}')
                return
            data = (await res.json())['list']
            embeds = []

            def replace_links(text, max_length=1024, characters_to_use=1000):
                def pred(m):
                    word = m.group(2)
                    return f'[{word}](https://www.urbandictionary.com/define.php?term={quote(word)})'

                text = self.URBAN_LINK_EXP.sub(pred, text)
                if len(text) >= max_length:
                    text = text[0:characters_to_use] + '...**snippet**'
                return text

            for item in data:
                print(item['word'])
                print(item['definition'])
                embed = discord.Embed(title=item['word'], description=replace_links(item['definition'], 2048, 2000),
                                      url=link, color=random_discord_color())
                example = replace_links(item["example"], 1024, 1000)
                embed.add_field(name="Example", value=example if example else 'No example available', inline=False)
                embed.set_footer(text="From Urban Dictionary")

                embeds.append(embed)

            if len(embeds) == 0:
                return await ctx.send('No data found')

            await BloodyMenuPages(EmbedPagesData(embeds)).start(ctx)

    @commands.command(aliases=["insult"])
    async def roast(self, ctx, *, member: discord.Member = None):
        """
        Insult that guy

        **Note**: These not meant to be taken seriously

        Args:
            member: The guy to insult
        """

        await ctx.channel.trigger_typing()
        member = member or ctx.author
        async with self.bot.clientSession.get("https://insult.mattbas.org/api/insult.json",
                                              headers={"Accept": "application/json"}) as res:
            if res.status != 200:
                await ctx.send("That lucky bastard... An error occurred."
                               "Mission failed bois, we'll get 'em next time")
                return
            insult = (await res.json(content_type="text/json"))['insult']
            await ctx.send(f'{member.mention}, {insult}')


def setup(bot):
    bot.add_cog(Internet(bot))
