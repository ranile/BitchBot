import discord
from discord.ext import commands

from util import funs, BloodyMenuPages, EmbedPagesData


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def arg_or_1(arg: str):
    return int(arg) if arg.isdigit() else 1


# noinspection PyIncorrectDocstring
class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["e"], invoke_without_command=True)
    async def emoji(self, ctx, emojis: commands.Greedy[discord.Emoji], amount: arg_or_1 = 1):
        """Send any number of the emoji given by 'emojis' command

        Args:
            emojis: The emojis to send.
            amount: The number of times to repeat
        """
        to_be_sent = ' '.join([f'{emoji} ' * amount for emoji in emojis])
        if to_be_sent == '':
            return await ctx.send('No emojis of that name found', delete_after=2)
        await ctx.send(to_be_sent)
        await ctx.message.delete(delay=2)

    @emoji.command(aliases=["emojiurl", "l"])
    async def link(self, ctx, emoji: discord.Emoji):
        """Send link of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to link
        """

        await ctx.send(emoji.url)
        await ctx.message.delete(delay=2)

    @emoji.command()
    async def list(self, ctx):
        """Shows the emojis that can be sent by 'emoji' command"""
        emojis = [e for e in self.bot.emojis if e.available]
        chunked_emojis = list(chunks(emojis, 20))
        count = 1
        data = []
        for emojis in chunked_emojis:
            embed = discord.Embed(title='Available emojis', color=funs.random_discord_color())
            embed.set_footer(text=f'Total: {len(emojis)}')
            out = []
            for emoji in emojis:
                out.append(f'{count}. {emoji.name} \t{emoji}')
                count += 1

            embed.description = '\n'.join(out)
            data.append(embed)

        pages = BloodyMenuPages(EmbedPagesData(data))
        await pages.start(ctx)

    @emoji.command(aliases=['em'])
    async def embed(self, ctx, emoji: discord.Emoji):
        """
        Send embed of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to send in an the embed
        """

        embed = discord.Embed()
        embed.set_image(url=str(emoji.url))
        await ctx.send(embed=embed)
        await ctx.message.delete(delay=2)

    @emoji.command()
    async def react(self, ctx, message: discord.Message, emoji: discord.Emoji):
        await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Emojis(bot))
