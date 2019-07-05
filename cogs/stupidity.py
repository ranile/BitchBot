from discord.ext import commands
import discord

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

def setup(bot):
    bot.add_cog(Stupidity(bot))

