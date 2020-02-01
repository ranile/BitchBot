import discord
from discord.ext import commands

from util import funs, BloodyMenuPages, EmbedPagesData


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# noinspection PyIncorrectDocstring
class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["e"], invoke_without_command=True)
    async def emoji(self, ctx, *emojis):
        """Send any number of the emoji given by 'emojis' command

        Args:
            emojis: The emoji to send. If the last value is a number, it repeats the every emoji that amount of times.
        """

        emojis = list(emojis)
        if str(emojis[-1]).isdigit():
            amount = int(emojis[-1])
            emojis.pop()
        else:
            amount = 1

        out = []
        for emoji in emojis:
            out.append(f'{discord.utils.get(self.bot.emojis, name=emoji)}' * amount)

        await ctx.send(' '.join(out))
        await ctx.message.delete(delay=2)

    @emoji.command(aliases=["emojiimg", "emoji1"])
    async def link(self, ctx, emoji):
        """Send link of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to link
        """

        await ctx.send(discord.utils.get(self.bot.emojis, name=emoji).url)
        await ctx.message.delete(delay=2)

    @emoji.command()
    async def list(self, ctx):
        """Shows the emojis that can be sent by 'emoji' command"""

        chunked_emojis = list(chunks(self.bot.emojis, 20))
        count = 1
        data = []
        for emojis in chunked_emojis:
            embed = discord.Embed(title='Available emojis', color=funs.random_discord_color())
            embed.set_footer(text='@hamza to add more')
            out = []
            for emoji in emojis:
                out.append(f'{count}. {emoji.name} \t{emoji}')
                count += 1

            embed.description = '\n'.join(out)
            data.append(embed)

        pages = BloodyMenuPages(EmbedPagesData(data))
        await pages.start(ctx)

    @emoji.command(aliases=["emoji2"])
    async def embed(self, ctx, emoji):
        """
        Send embed of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to send in an the embed
        """

        emoji = discord.utils.get(self.bot.emojis, name=emoji)
        await ctx.message.delete(delay=2)

        embed = discord.Embed()
        embed.set_image(url=str(emoji.url))
        await ctx.send(embed=embed)
        await ctx.message.delete(delay=2)


def setup(bot):
    bot.add_cog(Emojis(bot))
