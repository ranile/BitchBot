from discord.ext import commands
import discord
import requests
import os
import json

SAVE_USER_INFO_LINK = os.environ['ADD_USER_INFO_LINK']

GET_USER_INFO_LINK = os.environ['GET_USER_INFO_LINK']

USER_ROLE = os.environ['USER_ROLE']

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = json.loads(os.environ["QUESTIONS"])
        self.intro_result = {}

        # guild id and id of introduction channel of my server
        self.server_guild_id = os.environ['SERVER_GUILD_ID']
        self.introduction_cnl_id = os.environ['INTRODUCTION_CHANNEL_ID']
        self.welcome_cnl_id = os.environ['WELCOME_CHANNEL_ID']
        self.infromation_cnl_id = os.environ['INFORMATION_CHANNEL_ID']

    
    @commands.command()
    async def introduce(self, ctx):
        """
        Asks user for their introduction
        """
        if ctx.channel.guild.id != self.server_guild_id:
            return
        
        if ctx.channel.guild.id == self.server_guild_id and ctx.channel.id != self.introduction_cnl_id:
            await ctx.send(f'Wrong channel. Run this command in {self.bot.get_channel(self.introduction_cnl_id).mention}')
            return

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        intro_result = {}
        intro_result['id'] = str(ctx.author.id)
        for tag, question in self.questions.items():
            await ctx.send(question)
            msg = await self.bot.wait_for('message', check=pred)
            intro_result[tag] = msg.content

        requests.post(SAVE_USER_INFO_LINK, json = intro_result)
        await ctx.author.add_role(USER_ROLE)
        print(intro_result)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member):
        """
        Give user information
        """
        print(user.id)
        await ctx.channel.trigger_typing()
        req = requests.get(f'{GET_USER_INFO_LINK}?id={user.id}')
        data = req.json()
        embed = discord.Embed(title = data['name'])
        embed.add_field(name='Age:', value=data['age'], inline=True)
        embed.add_field(name='Invited by:', value=data['invited_by'], inline=True)
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == self.server_guild_id:
            welcome_cnl = self.bot.get_channel(self.welcome_cnl_id) 
            infromation_cnl = self.bot.get_channel(self.infromation_cnl_id)
            introduction_cnl = self.bot.get_channel(self.introduction_cnl_id)
            msg = f"Welcome to `server.name` member.mention!\nPlease refer to {infromation_cnl.mention} for all you need to know and use command `>introduce` to introduce yourself in {introduction_cnl.mention}"
            await welcome_cnl.send(msg)

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