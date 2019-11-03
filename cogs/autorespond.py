from discord.ext import commands
from keys import EPIC_EMOJIS_LINK, QUOTES_CHANNELS, SET_QUOTES_CHANNEL, COUNTERS_FOR_SERVER, UPDATE_COUNTER, COUNTERS
import discord, re, random, requests, asyncio


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

class AutoresponderCounterQuotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        req = requests.get(EPIC_EMOJIS_LINK)
        data = req.json()
        self.epic_emojis = []
        for i in data:
            self.epic_emojis.append(i['command'])

        self.quotes_channels = requests.get(QUOTES_CHANNELS).json()
        self.starred_messages = []

        print(self.quotes_channels)

        data = requests.get(COUNTERS).json()
        print(data)
        self.counters = {}

        for i in data:
            self.counters[i['name']] = i['count']
        
        print(self.counters)


    @commands.command()
    async def ping(self, ctx):
        """
        Ping Pong
        """
        await ctx.send("Pong")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        msg = ctx.content.lower()
        cnl = ctx.channel

        if ctx.author == self.bot.user:
            return
        
        if re.search(r"good (bitch)?bot", msg):
            await cnl.send(random.choice(["Dank you", "Aww", "Well you're breathtaking"]))

        elif re.search(r"(bad|stfu|fuck you) (bitch)? ?bot", msg):
            await cnl.send(random.choice(["Rip", "K", "You sure about that?", seals, "F", "😦"]))

        elif re.fullmatch(r"\bcreeper\b", msg):
            await cnl.send('Aww man')

        elif re.search(r"\b69\b", ctx.clean_content):
            await cnl.send("Ha thats the sex number")

        elif re.search(r"\b4:?20\b", ctx.clean_content):
            await cnl.send("Ha thats the weed number")

        if (random.randint(0,4) > 2):

            if (re.search(r"\be(p|b)?ic\b", msg)) and 'not epic' not in msg:
                emoji = random.choice(self.epic_emojis)
                await cnl.send(emoji)

            elif re.search(r"\bbruh(mius)?( moment(ium)?)?\b", msg):
                await cnl.send(random.choice(["THAT is a bruh moment", "<:bruh:610799376377577473>", "Epic bruh moment"]))

            elif re.search(r"\brip\b", msg):
                await cnl.send("Not epic")

            elif re.search(r"\bnot epic\b", msg):
                await cnl.send(random.choice(["Not epic, indeed", "rip"]))

            elif re.search(r"\buh oh\b", msg):
                await cnl.send("We're in danger")

            elif re.fullmatch(r"\bsmh\b", msg):
                await cnl.send(random.choice(["Shaking my smh", "Smh my head", "Ikr", "Shaking my head"]))

        for counter in self.counters.keys():
            rabbitMatch = r"(kaylie'?s? ?(man)|rabbit(man)?)"
            if (str(counter).lower() == 'rabbit') and re.search(rabbitMatch, msg, re.IGNORECASE):
                self.counters[counter] += 1
                requests.post(UPDATE_COUNTER, json={
                    'serverId': str(cnl.guild.id),
                    'counter': counter,
                    'value': self.counters[counter],
                })

                channel = cnl.guild.get_channel(int(self.quotes_channels[str(cnl.guild.id)]))
                await channel.send(f"Someone said rabbit {THE_RABBIT}, the Kaylie's man.\n{counter} count: {self.counters[counter]}")
                ctx.add_reaction(THE_RABBIT)
                return


            if str(counter).lower() in msg:
                self.counters[counter] += 1
                requests.post(UPDATE_COUNTER, json={
                    'serverId': str(cnl.guild.id),
                    'counter': counter,
                    'value': self.counters[counter],
                })

                channel = cnl.guild.get_channel(int(self.quotes_channels[str(cnl.guild.id)]))
                await channel.send(f'Someone said {counter}.\n{counter} count: {self.counters[counter]}')
    

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print('str(reaction)')
        print(str(reaction))

        if str(reaction) == "📌":
            await reaction.message.pin()
            await reaction.message.remove_reaction(reaction, user)
            await reaction.message.channel.send(f"{user.mention} Pinned a message!")

        elif str(reaction) == "⭐":

           
            if reaction.count < 2:
                print('nope')
                return
            if reaction.message.id in self.starred_messages:
                print('nah')
                return
            
            guild = reaction.message.channel.guild
            cnl = guild.get_channel(int(self.quotes_channels[str(guild.id)]))
            url = reaction.message.jump_url
            
            embed = discord.Embed(title = 'Go to message',url = url)
            embed.set_footer(text=f"- {reaction.message.author.name}")
            embed.colour = discord.Color(value=random.randint(0, 16777215))

            content = reaction.message.content
            if content:
                embed.description = content

            attachments = reaction.message.attachments
            if attachments:
                embed.set_image(url=attachments[0].url)

            await cnl.send(embed = embed)
            self.starred_messages.append(reaction.message.id)
    
    @commands.is_owner()
    @commands.command()
    async def setQuotesChannel(self, ctx, channel: discord.TextChannel):
        req = requests.post(SET_QUOTES_CHANNEL, {
            'guildId': str(ctx.message.guild.id),
            'channelId': str(channel.id),
        })

        if req.status_code != 200:
            await ctx.send('An error occured while saving')
            return
        
        self.quotes_channels = requests.get(QUOTES_CHANNELS).json()
        
        await ctx.send('Saved')

def setup(bot):
    bot.add_cog(AutoresponderCounterQuotes(bot))

