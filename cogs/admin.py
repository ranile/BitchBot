from discord.ext import commands
import discord
import inspect


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def delete(self, ctx, message):
        msg = await ctx.channel.fetch_message(message)
        await msg.delete()


def setup(bot):
    bot.add_cog(Admin(bot))
