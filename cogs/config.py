import discord
from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def config(self, ctx):
        pass

    @config.group()
    async def starboard(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Config(bot))
