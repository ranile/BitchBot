from discord.ext import commands
from keys import functionsUrl
import discord, re, random, requests, asyncio, unicodedata
from fuzzywuzzy import fuzz


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

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
THE_CAUSE = 505655510263922700
immune_to_rabbit = [529535587728752644, 453068315858960395]

ignoreAutorespond = {529349973998043146}

def chance(val):
    return random.randint(0, 4) > val

def isInAutorespondIgnore(message):
    return message.channel.guild.id in ignoreAutorespond

def fuzzy_rabbit_check(msg, ratioCheck):
    words = msg.split()
    for word in words:
        if not word.startswith("r") or word == 'r':
            continue
        
        ratio = fuzz.partial_ratio(word.lower(), 'rabbit')
        if ratio >= ratioCheck:
            return True
    
    return False


class AutoresponderCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(functionsUrl)
        self.epic_emojis = requests.get(f'{functionsUrl}/emojis/epic').json()

        self.quotes_channels = requests.get(f'{functionsUrl}/counters/channels').json()
        print(self.quotes_channels)

        self.counters = requests.get(f'{functionsUrl}/counters').json()
        print(self.counters)

        # Rabbit stuff
        self.rabbitRatio = 85
        self.isRabbitOnCooldown = False
        self.rabbitCooldownTime = 60
        self.rabbitAlreadySummoned = []

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
                emoji = random.choice(self.epic_emojis)
                await cnl.send(emoji)

            elif re.search(r"\bbruh(mius)?( moment(ium)?)?\b", msg) and chance(3):
                await cnl.send(random.choice(["THAT is a bruh moment", "<:bruh:610799376377577473>"]))

            elif re.search(r"\brip\b", msg) and chance(3):
                await cnl.send("Not epic")

            elif re.search(r"\bnot epic\b", msg) and chance(3):
                await cnl.send(random.choice(["Not epic, indeed", "rip"]))

            elif re.search(r"\buh oh\b", msg) and chance(3):
                await cnl.send("We're in danger")

        for counter in self.counters.keys():
            rabbitMatch = r"(kaylie'?s? ?(man)|r( +)?(a|@)( +)?b( +)?b( +)?i( +)?t(man)?|r ?word)"
            normalized = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')
            if (
                (str(counter).lower() == 'rabbit') and
                (re.search(rabbitMatch, normalized, re.IGNORECASE) or fuzzy_rabbit_check(normalized, self.rabbitRatio)) and
                cnl.guild.id == THE_CAUSE
            ):
                self.counters[counter] += 1
                if not self.isRabbitOnCooldown:
                    requests.patch(f'{functionsUrl}/counters/', json={
                        'serverId': str(cnl.guild.id),
                        'counter': counter,
                        'value': self.counters[counter],
                    })

                    channel = cnl.guild.get_channel(int(self.quotes_channels[str(cnl.guild.id)]))
                    rabbit = random.choice(rabbits)
                    await channel.send(f"{ctx.author.display_name} called the rabbit {rabbit}, Kaylie's man.\n{counter} count: {self.counters[counter]}")
                    await ctx.add_reaction(rabbit)
                    self.isRabbitOnCooldown = True
                    await asyncio.sleep(self.rabbitCooldownTime)
                    self.isRabbitOnCooldown = False
                    return


            if str(counter).lower() in msg and 'rabbit' not in msg:
                self.counters[counter] += 1
                requests.patch(f'{functionsUrl}/counters/', json={
                    'serverId': str(cnl.guild.id),
                    'counter': counter,
                    'value': self.counters[counter],
                })

                channel = cnl.guild.get_channel(int(self.quotes_channels[str(cnl.guild.id)]))
                await channel.send(f'Someone said {counter}.\n{counter} count: {self.counters[counter]}')
    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user.id == self.bot.user.id:
            return

        guild = reaction.message.channel.guild

        if str(reaction) == "📌":
            await reaction.message.pin()
            await reaction.message.remove_reaction(reaction, user)
            await reaction.message.channel.send(f"{user.mention} Pinned a message!")

        elif str(reaction) in rabbits:
            if reaction.message.id in self.rabbitAlreadySummoned:
                return

            channel = guild.get_channel(int(self.quotes_channels[str(guild.id)]))

            if not self.isRabbitOnCooldown:
        
                self.counters['rabbit'] += 1
                requests.patch(f'{functionsUrl}/counters/', json={
                    'serverId': str(guild.id),
                    'counter': 'rabbit',
                    'value': self.counters['rabbit'],
                })

                rabbit = [r for r in rabbits if r != str(reaction)][0]
                await channel.send(f"{user.display_name} summoned the rabbit {rabbit}, Kaylie's man.\nRabbit count: {self.counters['rabbit']}")
                await reaction.message.add_reaction(rabbit)

                self.rabbitAlreadySummoned.append(reaction.message.id)
                self.isRabbitOnCooldown = True
                await asyncio.sleep(self.rabbitCooldownTime)
                self.isRabbitOnCooldown = False
            
            else:
                self.counters['rabbit'] += 1


    @commands.is_owner()
    @commands.command()
    async def setCountersChannel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel to send the counter updates into for the guild

        Args:
            channel: The channel to send counter increment messages in
        """

        req = requests.post(f'{functionsUrl}/counters/channel', {
            'guildId': str(ctx.message.guild.id),
            'channelId': str(channel.id),
        })

        if req.status_code != 200:
            await ctx.send('An error occured while saving')
            return
        
        self.quotes_channels = requests.get(f'{functionsUrl}/counters/channels').json()        
        
        await ctx.send('Saved')

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

    @commands.is_owner()
    @commands.command()
    async def setRabbitCooldownTime(self, ctx, time):
        """Set the time after which the rabbit reaction cooldown expires

        Args:
            time: New cooldown time in seconds
        """

        self.rabbitCooldownTime = int(time)
        await ctx.send(f"The rabbit cooldown will now last {time} seconds")

def setup(bot):
    bot.add_cog(AutoresponderCounter(bot))
