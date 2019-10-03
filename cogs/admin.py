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
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit, messages_of: discord.Member = None):
        if messages_of is None:
            deleted = await ctx.channel.purge(limit=int(limit))
        else:
            def check(m):
                return m.author == messages_of
            
            deleted = await ctx.channel.purge(limit=int(limit), check=check)
        
        deleted_of = set()
        for message in deleted:
            deleted_of.add(message.author.name)
        
        await ctx.send(f'Deleted {len(deleted)} message(s) by {deleted_of}', delete_after = 7)
        await ctx.message.delete(delay=2)

def setup(bot):
    bot.add_cog(Owner(bot))
