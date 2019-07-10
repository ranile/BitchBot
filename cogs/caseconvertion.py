from discord.ext import commands
import discord

class CaseConvertion(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command()
    async def totogglecase(self, ctx, *, msg):
        """
        Convert string to toggle case
        """
        out = ""
        message = str(msg)
        for i in range(0, len(message)):
            out += message[i].lower() if (i%2 == 0) else message[i].upper()
        
        await ctx.send(out)
    
    @commands.command(aliases=["yell"])
    async def touppercase(self, ctx, *, msg):
        """
        Convert string to toggle case
        """
        await ctx.send(str(msg).upper())
    
    @commands.command()
    async def addspaces(self, ctx, *, msg):
        """
        Adds 3 spaces in between every character
        """
        await ctx.send('   '.join(list(str(msg))))
    

def setup(bot):
    bot.add_cog(CaseConvertion(bot))

    