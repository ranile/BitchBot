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

    @commands.command()
    @commands.is_owner()
    async def exit(self, ctx):
        """Kill the bot
        """
        await ctx.send('Closing...')
        await self.bot.clientSession.close()
        await self.bot.close()
        await self.bot.loop.stop()


def setup(bot):
    bot.add_cog(Admin(bot))
