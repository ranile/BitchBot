import asyncio
import random
import typing
import string

import discord
import re
from urllib.parse import quote
from discord.ext import commands as dpy_commands

from BitchBot import BitchBot
from util import BloodyMenuPages, EmbedPagesData, checks, commands
import util

SUB_OR_USER_EXP = re.compile(r'/?[ru]/[\w-]+', re.IGNORECASE)
IS_IMAGE_REGEX = re.compile(r".*\.(jpg|png|gif)$")

FLIP_RANGES = [
    (string.ascii_lowercase, "ɐqɔpǝɟƃɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎz"),
    (string.ascii_uppercase, "ⱯᗺƆᗡƎᖵ⅁HIᒋ⋊ꞀWNOԀꝹᴚS⊥ႶɅMX⅄Z"),
    (string.digits, "0ІᘔƐᔭ59Ɫ86"),
    (string.punctuation, "¡„#$%⅋,)(*+'-˙/:؛>=<¿@]\\[ᵥ‾`}|{~"),
]

CHAR_TO_FLIPPED = {}
for straight, gay in FLIP_RANGES:  # dw about it
    for i, character in enumerate(straight):
        CHAR_TO_FLIPPED[character] = gay[i]


def valid_sub_or_user(arg: str) -> str:
    match = SUB_OR_USER_EXP.fullmatch(arg)
    if match is None:
        raise dpy_commands.BadArgument(f'{arg} is not a valid a subreddit or username.'
                                       'Try something like r/sub or /u/username')
    name = match.group(0)
    if name.startswith('/'):
        name = name[1:]
    if name.endswith('/'):
        name = name[:-1]
    return name.lower()


def hot_or_new(arg: str) -> str:
    if arg.lower() not in ('hot', 'new'):
        raise dpy_commands.BadArgument(f'{arg} must be either `hot` or `new`')
    return arg.lower()


def must_be_between_0_and_13(arg: str) -> int:
    try:
        arg = int(arg)
    except ValueError:
        raise dpy_commands.BadArgument(f'{arg} is not a valid number')

    if arg > 13:
        raise dpy_commands.BadArgument(f'The columns and rows are cannot be more than 13')

    if arg < 1:
        raise dpy_commands.BadArgument(f'Provided number cannot be 0 or a negative number')

    return arg


# noinspection PyIncorrectDocstring
class Fun(dpy_commands.Cog):
    """
    Houses most of the fun commands
    """

    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot

    @commands.command()
    async def joke(self, ctx: commands.Context):
        """
        They are horrible. Seriously
        """

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://icanhazdadjoke.com",
                                        headers={"Accept": "application/json"}) as res:
            content = await res.json()
            await ctx.send(content['joke'])

    @commands.command()
    async def reddit(self, ctx: commands.Context, hot_new: typing.Optional[hot_or_new] = 'new', *,
                     search: valid_sub_or_user):
        """
        Get a random reddit post

        Args:
            search: The sub reddit or user from where you want to get the posts
        """

        await ctx.channel.trigger_typing()
        async with self.bot.session.get(f'http://reddit.com/{search}/{hot_new}/.json',
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
                                      color=util.random_discord_color())
                embed.set_author(name=f'u/{post["author"]}')
                embed.set_footer(text=post['subreddit_name_prefixed'])

                if post['is_self']:
                    text = post['selftext']
                    embed.description = text[:800] if len(text) < 800 else f'{text[:800]} **--Snippet--**'
                elif re.match(IS_IMAGE_REGEX, post['url']):
                    embed.set_image(url=post['url'])

                embeds.append(embed)

            if over_18 == total_posts:
                return await ctx.send('All posts found were NSFW. Try in an NSFW channel')
        await BloodyMenuPages(EmbedPagesData(embeds)).start(ctx)

    @commands.command()
    async def fact(self, ctx: commands.Context):
        """
        Fun fact. U gey
        """

        await ctx.channel.trigger_typing()
        async with self.bot.session.get("https://useless-facts.sameerkumar.website/api") as res:
            await ctx.send(((await res.json())['data']))

    @commands.command(aliases=('belikebill',))
    async def bill(self, ctx: commands.Context, *, name: typing.Union[str, discord.Member] = 'Bill'):
        """
        Be like bill

        Args:
            name: Server member or a name to get bill for
        """
        if isinstance(name, discord.Member):
            name = name.display_name
        link = f"https://belikebill.ga/billgen-API.php?default=1&name={quote(name)}"
        await ctx.send(embed=discord.Embed().set_image(url=link))

    URBAN_LINK_EXP = re.compile(r'(\[(.+?)\])')

    @commands.command()
    @checks.nsfw_only_in_non_trusted_guilds()
    async def urban(self, ctx: commands.Context, *, query: str):
        """
        Gets top definition from urban dictionary
        
        Args:
            query: A word you want to get defined
        """

        await ctx.channel.trigger_typing()
        search = quote(query)
        link = f"https://www.urbandictionary.com/define.php?term={search}"

        async with self.bot.session.get(f"http://api.urbandictionary.com/v0/define",
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
                                      url=link, color=util.random_discord_color())
                example = replace_links(item["example"], 1024, 1000)
                embed.add_field(name="Example", value=example if example else 'No example available', inline=False)
                embed.set_footer(text="From Urban Dictionary")

                embeds.append(embed)

            if len(embeds) == 0:
                return await ctx.send('No data found')

            await BloodyMenuPages(EmbedPagesData(embeds)).start(ctx)

    @commands.command(aliases=["insult"])
    async def roast(self, ctx: commands.Context, *, member: discord.Member = None):
        """
        Insult that guy

        **Note**: These not meant to be taken seriously

        Args:
            member: The guy to insult
        """

        await ctx.channel.trigger_typing()
        member = member or ctx.author
        async with self.bot.session.get("https://insult.mattbas.org/api/insult.json",
                                        headers={"Accept": "application/json"}) as res:
            if res.status != 200:
                await ctx.send("That lucky bastard... An error occurred."
                               "Mission failed bois, we'll get 'em next time")
                return
            insult = (await res.json(content_type="text/json"))['insult']
            await ctx.send(f'{member.mention}, {insult}')

    @commands.command(name='addspaces', aliases=["wide"], hidden=True)
    async def add_spaces(self, ctx: commands.Context, msg: str, spaces: int = 3):
        """
        Adds spaces in between every character.

        This command can only be used bot admins

        Args:
            msg: Message you want to make wide
            spaces: optional number of spaces between characters
        """

        between = spaces * ' '
        await ctx.send(embed=discord.Embed(description=between.join(list(msg)))
                       .set_author(name=str(ctx.author.display_name), icon_url=str(ctx.author.avatar_url)))

    @commands.command(hidden=True)
    async def flip(self, ctx: commands.Context, *, text: str):
        """
        Converts given text to flipped unicode characters

        This command can only be used bot admins

        Args:
            text: Message you want to flip
        """
        out = []
        for char in text:
            try:
                out.append(CHAR_TO_FLIPPED[char])
            except KeyError:
                out.append(char)

        await ctx.send(embed=discord.Embed(description=' '.join(out))
                       .set_author(name=str(ctx.author.display_name), icon_url=str(ctx.author.avatar_url)))

    @commands.command(aliases=["rick", "rickroll"])
    async def rickroulette(self, ctx: commands.Context):
        """
        Rickroll
        """
        await ctx.channel.trigger_typing()
        rick = "https://tenor.com/view/never-gonna-give-you-up-dont-give-never-give-up-gif-14414705"
        await asyncio.sleep(3)
        await ctx.send(f"Get rick rolled\n {rick}")

    @commands.command()
    async def owoize(self, ctx: commands.Context, *, text: str):
        """
        Owoizes the given text

        Args:
            text: A message you want to owoize
        """

        async with self.bot.session.get('https://nekos.life/api/v2/owoify', params={'text': text}) as resp:
            json = await resp.json()
            await ctx.send(json['owo'])

    @commands.command()
    async def swear(self, ctx: commands.Context, *, sentence: str):
        """
        Swear too much... or more like fuck a sentence

        Args:
            sentence: The sentence you wanna fuck up (add swear words to)
        """

        new = ''
        newsplitted = []
        splitted = sentence.split(' ')
        words = ['bitch', 'motherfucker', 'gay', 'fucker', 'boi', 'goddamn']
        end_words = [', okay bitch?!', ', now shut up', ', sit down boi']
        for x in splitted:
            newsplitted.append(x)
            if random.randint(0, 1):
                newsplitted.append(random.choice(words))
        for x in ' '.join(newsplitted):
            if random.randint(0, 1):
                new += x.upper()
            else:
                new += x.lower()
        if random.randint(0, 8) > 5:
            for x in random.choice(end_words):
                if random.randint(0, 1):
                    new += x.upper()
                else:
                    new += x.lower()
        await ctx.send(embed=discord.Embed(description=new).set_author(name=str(ctx.author.display_name),
                                                                       icon_url=str(ctx.author.avatar_url)))

    @commands.command(hidden=True)
    async def totogglecase(self, ctx: commands.Context, *, text: str):
        """
        Convert string to toggle case

        This command can only be used bot admins

        Args:
            text: Message you want to be in toggled case
        """
        out = []
        # hey python, fix your scoping. if a var is declared inside a loop,
        # yeet it once done with loop, kthx bye
        # noinspection PyShadowingNames
        for i, char in enumerate(text):
            out += char.lower() if (i % 2 == 0) else char.upper()

        await ctx.send(embed=discord.Embed(description=''.join(out))
                       .set_author(name=str(ctx.author.display_name), icon_url=str(ctx.author.avatar_url)))

    @commands.command(hidden=True)
    async def someone(self, ctx: commands.Context, *, text: str):
        """
        Repeats msg but with a random member's name after {prefix}someone

        Example:
            `{prefix}someone isn't cool

        Args:
            text: The text to be repeated
        """

        emote = random.choice(util.SOMEONE_EMOJIS)
        user = random.choice(ctx.guild.members).display_name
        response = f'@someone {emote} ***({user})*** {text}'
        await ctx.send(response)

    @commands.command(usage='[columns=random] [rows=random] [bombs=random]')
    @dpy_commands.max_concurrency(1, dpy_commands.BucketType.guild)
    async def minesweeper(
            self, ctx: commands.Context,
            columns: must_be_between_0_and_13 = random.randint(4, 13),
            rows: must_be_between_0_and_13 = random.randint(4, 13),
            bombs: int = None
    ):
        """
        Play a game of minesweeper

        Args:
            columns: The number of columns to have
            rows: The number of rows to have
            bombs: The number of bombs to have
        """
        if bombs is None:
            bombs = round(random.randint(5, round((columns * rows - 1) / 2.5)))

        if bombs + 1 > columns * rows:
            raise dpy_commands.BadArgument('You have more bombs than spaces on the grid or '
                                           'you attempted to make all of the spaces bombs!')

        def mapper(ch):
            return f'||{util.NUMBER_TO_LETTER.get(ch, "💣")}||'

        grid = [[0 for _ in range(columns)] for _ in range(rows)]

        for _ in range(bombs):
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)

            if grid[y][x] == 0:
                grid[y][x] = 'B'

        for i, gird_rows in enumerate(grid):
            for j, item in enumerate(gird_rows):
                picked = random.choice([x for x in range(0, 9)])
                if grid[i][j] != 'B':
                    grid[i][j] = picked

        game = '\n'.join((''.join(map(mapper, the_rows)) for the_rows in grid))

        await ctx.send(embed=discord.Embed(
            title='Minesweeper',
            description=f'{game}\n'
                        f'Columns: {columns}\n'
                        f'Rows: {rows}\n'
                        f'Bomb count/percentage: {bombs}/{round((bombs / (columns * rows)) * 100, 2)}\n'
        ).set_author(name=ctx.author.display_name, icon_url=str(ctx.author.avatar_url)))


def setup(bot):
    bot.add_cog(Fun(bot))
