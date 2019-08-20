from discord.ext import commands
import discord
import requests

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = {
            "name": "What's your name",
            "age": "How old are you",
            "invited_by": "Who invited you"
        }
        self.intro_result = {}

        # guild id and id of introduction channel of my server
        self.server_guild_id = 612627243239342080
        self.introduction_cnl_id = 613376365332267023
    
    @commands.command()
    async def introduce(self, ctx):
        """
        Asks user for their introduction
        """
        if ctx.channel.guild.id == self.server_guild_id and ctx.channel.id != self.introduction_cnl_id:
            await ctx.send(f'Wrong channel. Run this command in {self.bot.get_channel(self.introduction_cnl_id).mention}')
            return

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        author_id = str(ctx.author.id)
        self.intro_result[author_id] = {}

        for tag, question in self.questions.items():
            await ctx.send(question)
            msg = await self.bot.wait_for('message', check=pred)
            self.intro_result[author_id][tag] = msg.content


        print(self.intro_result) # save it to db

    @commands.command()
    async def userinfo(self, ctx, userid):
        """
        Give user information
        """
        await ctx.send(str(self.intro_result[userid]))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 612627243239342080: # guild id of my server
            welcome_cnl = self.bot.get_channel(613376350719442959) 
            infromation_cnl = self.bot.get_channel(613376875867406366)
            introduction_cnl = self.bot.get_channel(613376365332267023)
            msg = f"Welcome to `server.name` member.mention!\nPlease refer to {infromation_cnl.mention} for all you need to know and use command `>introduce` to introduce yourself in {introduction_cnl.mention}"
            await welcome_cnl.send(msg)
            
            # await member.add_role(member.guild.get_role(466645033437888512))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx,user: discord.Member, reason):
        """
        Kick a user
        Reason will show up on the audit log and will be dmed to the kicked user
        """

        embed = discord.Embed(title=f"You have been kicked from {ctx.guild.name}", description=reason)
        embed.set_footer(text=f"Kick by {ctx.author.display_name}" )
        embed.set_thumbnail(url=ctx.guild.icon_url)

        await user.send(embed=embed)
        await ctx.send(f"**User {user.mention} has been kicked by {ctx.author.mention}**")
        await user.kick(reason=reason) # Test if this works

def setup(bot):
    bot.add_cog(ServerManagement(bot))