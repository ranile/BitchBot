from discord.ext import commands
import discord
import random

RES_PATH = 'res/'

class Stupidity(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(aliases=["send"])
    async def say(self, ctx, *, message):
        """
        Have the bot say something. Have fun!
        """
        await ctx.send(message)

    @commands.command(aliases=["sendembed", "embed"])
    async def sayembed(self, ctx, *, message):
        """
        Have the bot say something in embeds. Have fun!
        """
        await ctx.send(embed = discord.Embed(description=message))

    @commands.command(aliases=["kayliesman"])
    async def rabbitman(self, ctx):
        """
        Sends a rabbitman picture
        """
        files = []
        for i in range(1, 10):
            files.append(f'{RES_PATH}rabbitman{i}.jpg')
        
        await ctx.channel.send(file=discord.File(files[random.randint(0,len(files)-1)]))

    @commands.command()
    async def baby(self, ctx):
        """
        Sends a Baby picture
        """
        files = []
        for i in range(1, 9):
            files.append(f'{RES_PATH}baby{i}.jpg')
        
        await ctx.channel.send(file=discord.File(files[random.randint(0,len(files)-1)]))

def setup(bot):
    bot.add_cog(Stupidity(bot))

