import random
import re
import discord
from discord.ext import commands

from services import EmojiService

seals = """What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of 
my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 
confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are 
nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been 
seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the 
Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is 
being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little 
thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven 
hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have 
access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your 
miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution 
your little "clever" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you 
couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will 
drown in it. You're fucking dead, kiddo. """

ignoreAutorespond = {529349973998043146}


def chance(val):
    # return random.randint(0, 4) > val
    return True


def isInAutorespondIgnore(message):
    return message.channel.guild.id in ignoreAutorespond


class Autoresponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.epic_emojis = None
        print(self.epic_emojis)

    async def setup(self):
        self.epic_emojis = await EmojiService.rawSelectQuery('''is_epic = true''')

    @commands.command()
    async def ping(self, ctx):
        """Ping Pong"""

        await ctx.send("Pong")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        msg = ctx.content.lower()
        cnl = ctx.channel

        if ctx.author == self.bot.user:
            return

        if not isInAutorespondIgnore(ctx):

            if re.search(r"good (bitch)?bot", msg):
                await cnl.send(random.choice(["Dank you", "Aww", "Well you're breathtaking"]))

            elif re.search(r"(bad|stfu|fuck you) (bitch)? ?bot", msg):
                await cnl.send(random.choice(["Rip", "K", "You sure about that?", seals, "F", "😦"]))

            elif re.fullmatch(r"\bcreeper\b", msg):
                await cnl.send('Aww man')

            elif re.search(r"\b69\b", ctx.clean_content):
                await cnl.send("Ha that's the sex number")

            elif re.search(r"\b4:?20\b", ctx.clean_content):
                await cnl.send("Ha that's the weed number")

            elif (re.search(r"\be(p|b)?ic\b", msg)) and 'not epic' not in msg and chance(2):
                emoji = random.choice(self.epic_emojis).command
                await cnl.send(emoji)

            elif re.search(r"\bbruh(mius)?( moment(ium)?)?\b", msg) and chance(3):
                await cnl.send(random.choice(["THAT is a bruh moment", "<:bruh:610799376377577473>"]))

            elif re.search(r"\brip\b", msg) and chance(3):
                await cnl.send("Not epic")

            elif re.search(r"\bnot epic\b", msg) and chance(3):
                await cnl.send(random.choice(["Not epic, indeed", "rip"]))

            elif re.search(r"\buh oh\b", msg) and chance(3):
                await cnl.send("We're in danger")

    @commands.is_owner()
    @commands.command()
    async def ignoreAutorespond(self, ctx):
        """Ignore autoresponder in current guild"""

        ignoreAutorespond.add(ctx.guild.id)
        await ctx.send(f'Ignoring {ctx.guild.name} until reload')

    @commands.is_owner()
    @commands.command()
    async def removeIgnoreAutorespond(self, ctx):
        """Remove current guild from autoresponder ignore"""

        ignoreAutorespond.remove(ctx.guild.id)
        await ctx.send(f'Removed autorespond ignore for {ctx.guild.name}')


def setup(bot):
    bot.add_cog(Autoresponder(bot))
