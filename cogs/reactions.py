from discord.ext import commands
import discord, requests

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quotes_channels = requests.get('http://localhost:5000/bitchbot-discordbot/us-central1/quotesChannels').json()
        self.starred_messages = []

        print(self.quotes_channels)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print('str(reaction)')
        print(str(reaction))

        if str(reaction) == "📌":
            await reaction.message.pin()
            await reaction.message.remove_reaction(reaction, user)
            await reaction.message.channel.send(f"{user.mention} Pinned a message!")

        elif str(reaction) == "⭐":

            print(reaction.count)
            
            if reaction.count < 2:
                print('nope')
                return
            if reaction.message.id in self.starred_messages:
                print('nah')
                return
            
            guild = reaction.message.channel.guild
            cnl = guild.get_channel(int(self.quotes_channels[str(guild.id)]))
            url = reaction.message.jump_url
            print(url)
            embed = discord.Embed(title = 'Go to message',url = url)
            embed.add_field(name  = 'Author', value = reaction.message.author.name, inline = True)
            embed.add_field(name  = 'Channel', value = reaction.message.channel.mention, inline = True)

            content = reaction.message.content
            if content:
                embed.add_field(name  = 'Content', value = content, inline = False)

            attachments = reaction.message.attachments
            if attachments:
                embed.set_image(url=attachments[0].url)

            await cnl.send(embed = embed)
            self.starred_messages.append(reaction.message.id)
    
    @commands.is_owner()
    @commands.command()
    async def setQuotesChannel(self, ctx, channel: discord.TextChannel):
        req = requests.post('http://localhost:5000/bitchbot-discordbot/us-central1/setQuotesChannel', {
            'guildId': str(ctx.message.guild.id),
            'channelId': str(channel.id),
        })

        if req.status_code != 200:
            await ctx.send('An error occured while saving')
            return
        
        self.quotes_channels = requests.get('http://localhost:5000/bitchbot-discordbot/us-central1/quotesChannels').json()
        
        await ctx.send('Saved')



def setup(bot):
    bot.add_cog(Reactions(bot))
