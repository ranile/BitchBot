import discord
from discord.ext import commands

from database import database
from resources import Emoji
from services import EmojiService
from util import funs, paginator


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# noinspection PyIncorrectDocstring
class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["emojiimg", "emoji1"])
    async def emojilink(self, ctx, emoji):
        """Send link of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to link
        """

        fetched = await EmojiService.get('name', emoji)
        await ctx.send(f"https://cdn.discordapp.com/emojis/{fetched.id}.{'gif' if fetched.isAnimated else 'png'}")
        await ctx.message.delete(delay=2)

    @commands.command(aliases=["e"])
    async def emoji(self, ctx, *emojis):
        """Send any one of the emoji given by 'emojis' command

        Args: emojis: The emoji to send. This can take variable number of value. If the last value is a number,
        it repeats the every emoji that amount of times
        """

        emojis = list(emojis)
        if str(emojis[-1]).isdigit():
            amount = int(emojis[-1])
            emojis.pop()
        else:
            amount = 1

        fetched = await EmojiService.rawSelectQuery(f'''name IN ({funs.generateDollarSigns(emojis)})''', emojis)

        out = ""
        for emoji in fetched:
            out += f'{emoji.command} ' * amount

        await ctx.send(out)
        await ctx.message.delete(delay=2)

    @commands.command()
    async def emojis(self, ctx):
        """Shows the emojis that can be sent by 'emoji' command"""

        fetched_emojis = await EmojiService.getAll()

        chunked_emojis = list(chunks(fetched_emojis, 20))
        count = 1
        data = []
        for emojis in chunked_emojis:
            embed = discord.Embed(title='Available emojis', color=funs.random_discord_color())
            embed.set_footer(text='@hamza to add more')
            out = []
            for emoji in emojis:
                out.append(f'{count}. {emoji.name} \t{emoji.command}')
                count += 1

            embed.description = '\n'.join(out)
            data.append(embed)

        pages = paginator.Paginator(ctx, data)
        await pages.paginate()

    @commands.command(aliases=["emoji2"])
    async def emojiembed(self, ctx, emoji):
        """
        Send embed of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to send in an the embed
        """

        fetched = await EmojiService.get('name', emoji)
        url = f"https://cdn.discordapp.com/emojis/{fetched.id}.{'gif' if fetched.isAnimated else 'png'}"
        await ctx.message.delete(delay=2)

        embed = discord.Embed()
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        await ctx.message.delete(delay=2)

    @commands.command()
    async def update_emojis(self, ctx):
        await database.connection.execute('''drop table if exists emojis''')
        await database.connection.execute('''
        CREATE TABLE IF NOT EXISTS Emojis (
            id bigint NOT NULL PRIMARY KEY,
            name text NOT NULL,
            command text NOT NULL,
            is_epic bool NOT NULL,
            is_animated bool NOT NULL
        );''')

        count = 0
        for emoji in self.bot.emojis[20:]:
            to_be_inserted = Emoji(
                name=emoji.name,
                command=str(emoji),
                isAnimated=emoji.animated,
                isEpic=False,
                id=emoji.id
            )

            await EmojiService.insert(to_be_inserted)
            count += 1

        await ctx.send(f'Added {count} emojis')

def setup(bot):
    bot.add_cog(Emojis(bot))
