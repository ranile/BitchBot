from discord.ext import commands
import discord

class CaseConversion(commands.Cog):
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
    
    @commands.command(aliases=["wide"])
    async def addspaces(self, ctx, *, msg):
        """
        Adds default 3 spaces in between every character.
        If a number is the first argument, that number of 
        spaces will be used.
        """
        arg = msg.split(" ")
        try:
            spaces = int(arg[0])
            msg = ' '.join(arg[1:])
        except:
            spaces = 3
        between = ' ' * spaces
        await ctx.send(between.join(list(str(msg))))
    

def setup(bot):
    bot.add_cog(CaseConversion(bot))

    