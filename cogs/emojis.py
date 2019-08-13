from discord.ext import commands
import discord
import json
import itertools
import re

RES_PATH = 'res/'

class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open(f'{RES_PATH}emojis.json') as f:
            emojis = json.load(f)
            self.animated_emojis_to_ids = emojis['animated_emojis_to_ids']
            self.animated_emojis = emojis['animated_emojis']
            self.emojis_to_ids = emojis['non_animated_emojis_to_ids']
            self.nona_emojis = emojis['non_animated_emojis']
    
    @commands.command(aliases=["emojilarge", "enlargeemoji"])
    async def emojiimg(self, ctx, message):
        """
        Send link of any one of the emoji given by 'emojis' command
        """
        if message in self.animated_emojis_to_ids.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.animated_emojis_to_ids[message]}.gif"
            await ctx.send(url)
        elif message in self.emojis_to_ids.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.emojis_to_ids[message]}.png"
            await ctx.send(url)
        else:
            await ctx.send('Emoji not available')

    @commands.command()
    async def emoji(self, ctx, message, amount=1):
        """
        Send any one of the emoji given by 'emojis' command
        """
        if int(amount) >= 71:
            await ctx.send(f'Too many bruh {self.nona_emojis["bruh"]} {self.animated_emojis["oof"]}')
            return
        if message in self.animated_emojis_to_ids.keys():
            await ctx.send(f'{self.animated_emojis[message]} '* amount)
        elif message in self.emojis_to_ids.keys():
            await ctx.send(f'{self.nona_emojis[message]} ' * amount)
        else:
            await ctx.send('Emoji not available')

    @commands.command()
    async def emojis(self, ctx):
        """
        Shows the emojis that can be sent by 'emoji' command
        """
        out_animated = ''
        out_non_animated = ''

        for i in range(0, len(self.animated_emojis_to_ids.keys())):
            emojis = list(self.animated_emojis_to_ids.keys())
            out_animated += f'{i+ 1}. {emojis[i]}: {self.animated_emojis[emojis[i]]}\n'
        
        for i in range(0, len(self.emojis_to_ids.keys())):
            emojis = list(self.emojis_to_ids.keys())
            out_non_animated += f'{i + 1}. {emojis[i]}: {self.nona_emojis[emojis[i]]}\n'
        
        embed=discord.Embed(title='Available emojis')
        embed.add_field(name='Animated:', value=out_animated, inline=False)
        embed.add_field(name='Non animated:', value=out_non_animated, inline=True)
        embed.set_footer(text='@hamza to add more')
        
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Emojis(bot))

