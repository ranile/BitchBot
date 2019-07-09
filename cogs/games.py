from discord.ext import commands
import discord
import random

class Games(commands.Cog):
    truths = []
    dares = []
    wouldyourather = []

    def __init__(self, bot): 
        self.bot = bot
        with open("res/truth.txt", encoding="utf8") as f:
            self.truths = f.read().splitlines()
    
        with open("res/dare.txt", encoding="utf8") as f:
            self.dares = f.read().splitlines()

        with open('res/wyr.txt', encoding="utf8") as f:
            self.wouldyourather = f.read().splitlines()

    @commands.command()
    async def truth(self, ctx):
        """
        Speak truth
        """
        await ctx.send(str(self.truths[random.randint(0, len(self.truths))]).strip())

    @commands.command()
    async def dare(self, ctx):
        """
        Do it, bitch
        """
        await ctx.send(str(self.dares[random.randint(0, len(self.dares))]).strip())

    @commands.command()
    async def wyr(self, ctx):
        """
        Answer me
        """
        await ctx.send(str(self.wouldyourather[random.randint(0, len(self.wouldyourather))]).strip())

def setup(bot):
    bot.add_cog(Games(bot))

