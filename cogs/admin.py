from discord.ext import commands
import discord


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module):
        self.bot.reload_extension(module)
        await ctx.send("🔄")

    @commands.is_owner()
    @commands.command()
    async def delete(self, ctx, message):
        msg = await ctx.channel.fetch_message(message)
        await msg.delete()
    
    @commands.command()
    async def y(self, ctx, id):
        msg = await ctx.channel.fetch_message(id)
        await msg.add_reaction('⭐')
        # cnl = ctx.message.channel.guild.get_channel(627144637328392192)
        # his = await cnl.history(limit=100).flatten()
        # for i in his:
        #     print(i.author, i.content)

def setup(bot):
    bot.add_cog(Owner(bot))
