from discord.ext import commands
import discord, requests, random
from keys import QUOTES_CHANNELS, SET_QUOTES_CHANNEL, COUNTERS_FOR_SERVER, UPDATE_COUNTER

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes_channels = requests.get(QUOTES_CHANNELS).json()
        self.starred_messages = []

        print(self.quotes_channels)

        data = requests.get(f'{COUNTERS_FOR_SERVER}?serverId=607386356582187008').json()
        print(data)
        self.counters = {}

        for i in data:
            self.counters[i['name']] = i['count']
        
        print(self.counters)

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
    
    @commands.Cog.listener()
    async def on_message(self, ctx):

        if ctx.author == self.bot.user:
            return

        msg = ctx.content.lower()
        cnl = ctx.channel

        for counter in self.counters.keys():
            if str(counter).lower() in msg:
                self.counters[counter] += 1
                requests.post(UPDATE_COUNTER, json={
                    'serverId': str(cnl.guild.id),
                    'counter': counter,
                    'value': self.counters[counter],
                })

                channel = cnl.guild.get_channel(int(self.quotes_channels[str(cnl.guild.id)]))
                await channel.send(f'Someone said {counter}.\n{counter} count: {self.counters[counter]}')
                

def setup(bot):
    bot.add_cog(Reactions(bot))
