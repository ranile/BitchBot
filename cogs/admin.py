from discord.ext import commands
import discord


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(aliases=["send"])
    async def say(self, ctx, *, message):
        await ctx.send(message)

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module):
        self.bot.reload_extension("cog."+module)
        await ctx.send("🔄")



def setup(bot):
    bot.add_cog(Owner(bot))
