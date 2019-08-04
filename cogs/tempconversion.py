from discord.ext import commands
import discord

def c_to_f(c: float) -> float:
    return (c * 9/5) + 32

def f_to_c(f: float) -> float:
    return (f - 32) * (5/9)

class Temperature(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(aliases=["to_c"])
    async def toc(self, ctx, message):
        """
        Convert fahrenheit to celsius. Format: '>toc <temp in f>'. Example: '>toc 69'.
        """
        try:
            await ctx.send(f'{int(f_to_c(float(message)))}°C')
        except Exception as identifier:
            await ctx.send(f"Bruh...\nDon't you know how to follow instructions\nError: {identifier}")

    @commands.command(aliases=["to_f"])
    async def tof(self, ctx, message):
        """
        Convert celsius to fahrenheit. Format: '>tof <temp in c'. Example: '>tof 20.5'.
        """
        try:
            await ctx.send(f'{int(c_to_f(float(message)))}°F')
        except Exception as identifier:
            await ctx.send(f"Bruh...\nDon't you know how to follow instructions\nError: {identifier}")

def setup(bot):
    bot.add_cog(Temperature(bot))

