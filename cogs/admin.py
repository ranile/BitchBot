from discord.ext import commands
import discord


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module):
        self.bot.reload_extension("cog."+module)
        await ctx.send("🔄")

    @commands.is_owner()
    @commands.command()
    async def delete(self, ctx, message):
        msg = await ctx.channel.fetch_message(message)
        await msg.delete()
    
    @commands.is_owner()
    @commands.command()
    async def haunt(self, ctx, victim: discord.Member):
        await victim.send('Good morning')
        await victim.send('I heard you wanted me to stay out of your DMs')
        await victim.send('Wish granted')
        await victim.send('<:rabbitman:593375171880943636>')
        embed = discord.Embed()
        embed.set_image(url = 'https://github.com/hamza1311/BitchBot/blob/master/res/rabbitman7.jpg')
        await victim.send(embed = embed)
        embed2 = discord.Embed()
        embed2.set_image(url = 'https://github.com/hamza1311/BitchBot/blob/master/res/baby1.jpg')
        await victim.send(embed = embed2)



def setup(bot):
    bot.add_cog(Owner(bot))
