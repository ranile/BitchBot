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

    @commands.command(aliases=["kayliesman"])
    async def rabbitman(self, ctx):
        """
        Sends a rabbitman picture
        """
        await ctx.channel.send(file=discord.File('res/rabbitman.jpg'))

def setup(bot):
    bot.add_cog(Stupidity(bot))

