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
        await ctx.message.delete()
    
    @commands.command(aliases=["yell"])
    async def touppercase(self, ctx, *, msg):
        """
        Convert string to toggle case
        """
        await ctx.send(str(msg).upper())
        await ctx.message.delete()
    
    @commands.command(aliases=["wide"])
    async def addspaces(self, ctx, *, msg):
        """
        Adds 3 spaces in between every character.
        If the first arg is a number, it will use
        that for the number of spaces instead.
        """
        args = msg.split(" ")
        try:
            spaces = int(args[0])
            msg = ' '.join(args[1:])
        except ValueError:
            spaces = 3
        between = spaces * ' '
        await ctx.send(between.join(list(str(msg))))
        await ctx.message.delete()
    
    # @commands.command()
    # async def flip(self, ctx, *, msg):
    #     """
    #     Flip latin characters.
    #     """
    #     FLIP_RANGES = [
    #         (string.ascii_lowercase, "ɐqɔpǝɟƃɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎz"),
    #         # alternatives: l:ʅ
    #         (string.ascii_uppercase, "ⱯᗺƆᗡƎᖵ⅁HIᒋ⋊ꞀWNOԀꝹᴚS⊥ႶɅMX⅄Z"),
    #         # alternatives: L:ᒣ⅂, J:ſ, F:߃Ⅎ, A:∀ᗄ, U:Ⴖ, W:Ϻ, C:ϽↃ, Q:Ό, M:Ɯꟽ
    #         (string.digits, "0ІᘔƐᔭ59Ɫ86"),
    #         (string.punctuation, "¡„#$%⅋,)(*+'-˙/:؛>=<¿@]\\[ᵥ‾`}|{~"),
    #     ]

    #     chars = list(msg)
    #     msgBack = ""
    #     for c in chars:
    #         for r in range(len(FLIP_RANGES)):
    #             try:
    #                 p = FLIP_RANGES[r][0].index(c)
    #                 if not p == -1:
    #                     newC = FLIP_RANGES[r][1][p]
    #                     msgBack += newC
    #                     break
    #             except ValueError:
    #                 continue
    #     await ctx.send(msgBack)
    #     await ctx.message.delete()

def setup(bot):
    bot.add_cog(CaseConversion(bot))

    