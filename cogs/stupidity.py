from discord.ext import commands
import discord
import random
import itertools
import re

RES_PATH = 'res/'

class Stupidity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.regional_indicator = ":regional_indicator_"
        self.emoji_chars = {
            'a': '🇦',
            'b': '🇧',
            'c': '🇨',
            'd': '🇩',
            'e': '🇪',
            'f': '🇫',
            'g': '🇬',
            'h': '🇭',
            'i': '🇮',
            'j': '🇯',
            'k': '🇰',
            'l': '🇱',
            'm': '🇲',
            'n': '🇳',
            'o': '🇴',
            'p': '🇵',
            'q': '🇶',
            'r': '🇷',
            's': '🇸',
            't': '🇹',
            'u': '🇺',
            'v': '🇻',
            'w': '🇼',
            'x': '🇽',
            'y': '🇾',
            'z': '🇿'
        }

        self.emoji_chars_alts = {
            'k': "🎋",
            'l': "👢",
            'o': "⭕",
            'q': "🎯",
            's': "💲",        
            'u': "⛎",
            'x': "❌"
        }

        self.animated_emojis_to_ids = {
            'oof': 447819226795999233,
            'nou': 527620293976391691,
            'xAccept': 585833119672958998,
            '0PepeHowdy': 594175419801141273,
            'dance': 429336765933813781,
            '0SpookyPls': 608340245485846591,
            'ping': 605457745004724279
        }

        self.emojis_to_ids = {
            'arianafite': 607895287293411339
        }

    @commands.command(aliases=["send"])
    async def say(self, ctx, *, message):
        """
        Have the bot say something. Have fun!
        """
        await ctx.send(message)

    @commands.command(aliases=["sendembed", "embed"])
    async def sayembed(self, ctx, *, message):
        """
        Have the bot say something in embeds. Have fun!
        """
        await ctx.send(embed = discord.Embed(description=message))

    @commands.command(aliases=["kayliesman"])
    async def rabbitman(self, ctx):
        """
        Sends a rabbitman picture
        """
        files = []
        for i in range(1, 11):
            files.append(f'{RES_PATH}rabbitman{i}.jpg')
        
        await ctx.channel.send(file=discord.File(files[random.randint(0,len(files)-1)]))

    @commands.command()
    async def baby(self, ctx):
        """
        Sends a Baby picture
        """
        files = []
        for i in range(1, 9):
            files.append(f'{RES_PATH}baby{i}.jpg')
        
        await ctx.channel.send(file=discord.File(files[random.randint(0,len(files)-1)]))

    @commands.command()
    async def react(self, ctx, message, text):
        
        msg = await ctx.channel.fetch_message(message)
        sent = []
        for i in text:
            if re.fullmatch(r'[a-z]', i, re.IGNORECASE):
                emoji = str(i).lower()
                if (i in sent) and (emoji in self.emoji_chars_alts.keys()):
                    await msg.add_reaction(self.emoji_chars_alts[emoji])
                else:
                    await msg.add_reaction(self.emoji_chars[emoji])
                sent.append(i)  

    @commands.command()
    async def emoji(self, ctx, message):
        if message in self.animated_emojis_to_ids.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.animated_emojis_to_ids[message]}.gif"
            await ctx.send(url)
        elif message in self.emojis_to_ids.keys():
            url = f"https://cdn.discordapp.com/emojis/{self.emojis_to_ids[message]}.png"
            await ctx.send(url)
        else:
            await ctx.send('Emoji not available')

def setup(bot):
    bot.add_cog(Stupidity(bot))

