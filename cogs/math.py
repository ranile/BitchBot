from discord.ext import commands
import discord

class Maths(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command()
    async def add(self, ctx, *numbers):
        """
        Add. Format: '>add number1 number2 ...'
        """
        out = 0
        for number in numbers:
            if str(number).isdigit:
                out += int(number)
            else:
                await ctx.send('Give numbers to add bitch')
        
        await ctx.send(f'Result: {out}')

    @commands.command()
    async def subtract(self, ctx, *numbers):
        """
        Subtract number2 from number1. Format: '>subtract number1 number2'. Only 2 numbers allowed
        """

        await ctx.send(f'Result: {int(numbers[0]) - int(numbers[1])}')

    @commands.command()
    async def multiply(self, ctx, *numbers):
        """
        Multiply. Format: '>multiply number1 number2 ...'
        """
        out = 1
        for number in numbers:
            if str(number).isdigit:
                out *= int(number)
            else:
                await ctx.send('Give numbers to multiply bitch')
        
        await ctx.send(f'Result: {out}')

    @commands.command()
    async def divide(self, ctx, *numbers):
        """
        Divide number1 by number2. Format: '>divide number1 number2'. Only 2 numbers allowed
        """
        await ctx.send(f'Result: {int(numbers[0]) / int(numbers[1])}')

def setup(bot):
    bot.add_cog(Maths(bot))

