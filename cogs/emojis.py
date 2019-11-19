from discord.ext import commands
import discord, requests, itertools, re, random
from keys import EMOJIS_LINK

class AnimatedEmoji():
    def __init__(self, name, id, command):
        self.name = name
        self.id = id
        self.command = command

class UnAnimatedEmoji():
    def __init__(self, name, id, command):
        self.name = name
        self.id = id
        self.command = command

class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        res = requests.get(EMOJIS_LINK)
        json = res.json()

        self.animated_emojis = {}
        self.non_animated_emojis = {}

        for i in json:
            if i['isAnimated']:
                self.animated_emojis[i['name']] = AnimatedEmoji(i['name'], i['id'], i['command'])
            else:
                self.non_animated_emojis[i['name']] = UnAnimatedEmoji(i['name'], i['id'], i['command'])

    @commands.command(aliases=["emojiimg", "emoji1"])
    async def emojilink(self, ctx, emoji):
        """Send link of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to link
        """

        if emoji in self.animated_emojis.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.animated_emojis[emoji].id}.gif"
            await ctx.send(url)
        elif emoji in self.non_animated_emojis.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.non_animated_emojis[emoji].id}.png"
            await ctx.send(url)

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

        out = ""
        for message in emojis:
            if message in self.animated_emojis.keys():
                out += f'{self.animated_emojis[message].command} '* amount
            elif message in self.non_animated_emojis.keys():
                out += f'{self.non_animated_emojis[message].command} ' * amount

        await ctx.send(out)
        await ctx.message.delete(delay=2)        

    @commands.command()
    async def emojis(self, ctx):
        """Shows the emojis that can be sent by 'emoji' command"""

        out_animated = ''
        out_non_animated = ''

        for i in range(0, len(self.animated_emojis.keys())):
            emojis = list(self.animated_emojis.keys())
            out_animated += f'{i+ 1}. {emojis[i]}: {self.animated_emojis[emojis[i]].command}\n'
        
        for i in range(0, len(self.non_animated_emojis.keys())):
            emojis = list(self.non_animated_emojis.keys())
            out_non_animated += f'{i + 1}. {emojis[i]}: {self.non_animated_emojis[emojis[i]].command}\n'
        
        embed=discord.Embed(title='Available emojis')
        embed.add_field(name='Animated:', value=out_animated, inline=False)
        embed.add_field(name='Non animated:', value=out_non_animated, inline=True)
        embed.set_footer(text='@hamza to add more')
        embed.colour = discord.Color(value=random.randint(0, 16777215))
        
        await ctx.send(embed = embed)

    
    @commands.command(aliases=["emoji2"])
    async def emojiembed(self, ctx, emoji):
        """
        Send embed of any one of the emoji given by 'emojis' command

        Args:
            emoji: The emoji to send in an the embed
        """
        embed=discord.Embed()
        if emoji in self.animated_emojis.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.animated_emojis[emoji].id}.gif"
            embed.set_image(url=url)
            await ctx.send(embed=embed)

        elif emoji in self.non_animated_emojis.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.non_animated_emojis[emoji].id}.png"
            embed.set_image(url=url)
            await ctx.send(embed=embed)

        await ctx.message.delete(delay=2)
    
def setup(bot):
    bot.add_cog(Emojis(bot))

