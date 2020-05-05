from discord.ext import commands
import discord
import random
import itertools
import re

RES_PATH = 'res/'

class Stupidity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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

        self.someone_emotes = [u'\u0CA0_\u0CA0',
                               u'\u30FD\u0F3C \u0CA0\u76CA\u0CA0 \u0F3D\uFF89', 
                               u'\u00AF(\u00B0_o)/\u00AF',
                               u'\uFF08\u273F \u0361\u25D5 \u1D17\u25D5)\u3064\u2501\u2501\u272B\u30FBo\u3002', 
                               u'(\u256F\u00B0\u25A1\u00B0\uFF09\u256F\uFE35 \u253B\u2501\u253B',
                               u'\uFF08\u273F \u0361\u25D5 \u1D17\u25D5)\u3064\u2501\u2501\u272B\u30FBo\u3002',
                               u'\u0F3C \u3064 \u25D5_\u25D5 \u0F3D\u3064',
                               u'(\u2229 \u0361\u00B0 \u035C\u0296 \u0361\u00B0)\u2283\u2501',
                               u'\u00AF\_(\u30C4)_/\u00AF']

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

    @commands.command(aliases=["addreaction"])
    async def react(self, ctx, message, text):
        """
        Add the given reactions to a message
        """
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
    async def someone(self, ctx, *, text)
        """
        Repeats the message but with a random member's name after :someone
        """
        emote = choice(self.someone_emotes)
        user = choice(ctx.guild.members).display_name
        response = "@someone {} ***({})*** {}".format(emote, user, text)
        await ctx.send(response)

def setup(bot):
    bot.add_cog(Stupidity(bot))

