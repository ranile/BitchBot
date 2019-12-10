from discord.ext import commands
import discord
import random
from services import EmojiService
from util import funs


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

        Args:
            emojis: The emoji to send. This can take variable number of value. If the last value is a number, it repeats the every emoji that amount of times
        """

        emojis = list(emojis)
        if str(emojis[-1]).isdigit():
            amount = int(emojis[-1])
            emojis.pop()
        else:
            amount = 1

        dollarSigns = funs.generateDollarSigns(emojis)
        fetched = await EmojiService.rawSelectQuery(f'''name IN ({dollarSigns})''', emojis)

        out = ""
        for emoji in fetched:
            out += f'{emoji.command} ' * amount

        await ctx.send(out)
        await ctx.message.delete(delay=2)        

    @commands.command()
    async def emojis(self, ctx):
        """Shows the emojis that can be sent by 'emoji' command"""

        emojis = await EmojiService.getAll()

        print([str(x) for x in emojis])

        animated = [emoji for emoji in emojis if emoji.isAnimated]
        non_animated = [emoji for emoji in emojis if not emoji.isAnimated]
        print([str(x) for x in animated])
        print([str(x) for x in non_animated])
        print('-------------------')
        out_animated = ''
        out_non_animated = ''

        for i in range(0, len(animated)):
            out_animated += f'{i+ 1}. {emojis[i].name}: {animated[i].command}\n'
        
        for i in range(0, len(non_animated)):
            out_non_animated += f'{i+ 1}. {emojis[i].name}: {non_animated[i].command}\n'
        
        embed = discord.Embed(title='Available emojis')
        embed.add_field(name='Animated:', value=out_animated if out_animated != '' else 'None', inline=False)
        embed.add_field(name='Non animated:', value=out_non_animated if out_non_animated != '' else 'None', inline=True)
        embed.set_footer(text='@hamza to add more')
        embed.colour = discord.Color(value=random.randint(0, 16777215))  # TODO: Use the fun
        
        await ctx.send(embed = embed)

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


def setup(bot):
    bot.add_cog(Emojis(bot))

