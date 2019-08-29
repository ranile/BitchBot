from discord.ext import commands
import discord
import requests
import os
import json

SAVE_USER_INFO_LINK = os.environ['ADD_USER_INFO_LINK']

GET_USER_INFO_LINK = os.environ['GET_USER_INFO_LINK']

GET_SERVER_SELFASSIGN_ROLES_LINK = os.environ['GET_SERVER_SELFASSIGN_ROLES_LINK']

GET_ID_SELFASSIGN_LINK = os.environ['GET_ID_SELFASSIGN_LINK']

USER_ROLE = os.environ['USER_ROLE']

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = json.loads(os.environ["QUESTIONS"])
        self.intro_result = {}

        # guild id and id of introduction channel of my server
        self.server_guild_id = int(os.environ['SERVER_GUILD_ID'])
        self.introduction_cnl_id = int(os.environ['INTRODUCTION_CHANNEL_ID'])
        self.welcome_cnl_id = int(os.environ['WELCOME_CHANNEL_ID'])
        self.infromation_cnl_id = int(os.environ['INFORMATION_CHANNEL_ID'])

        self.tit = int(os.environ['TIT'])
        self.tit_main = int(os.environ['TIT_MAIN'])

    
    @commands.command()
    async def introduce(self, ctx):
        """
        Asks user for their introduction
        """
        # if ctx.channel.guild.id != self.server_guild_id:
        #     return
        tit_questions = os.environ["TIT_QUESTIONS"]

        if ctx.channel.guild.id == self.tit:
            iquestions = json.loads(tit_questions)
        else:
            iquestions = QUESTIONS
        
        if ctx.channel.guild.id == self.server_guild_id and ctx.channel.id != self.introduction_cnl_id:
            await ctx.send(f'Wrong channel. Run this command in {self.bot.get_channel(self.introduction_cnl_id).mention}')
            return

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        intro_result = {}
        intro_result['id'] = str(ctx.author.id)
        intro_result['serverId'] = str(ctx.channel.guild.id)
        for tag, question in iquestions.items():
            await ctx.send(question)
            msg = await self.bot.wait_for('message', check=pred)
            intro_result[tag] = msg.content

        requests.post(SAVE_USER_INFO_LINK, json = intro_result)
        if ctx.channel.guild.id == self.server_guild_id:
            await ctx.message.author.add_roles(ctx.channel.guild.get_role(USER_ROLE))
        await ctx.send('Welcome!')
        print(intro_result)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member):
        """
        Give user information
        """
        print(user.id)
        await ctx.channel.trigger_typing()
        req = requests.get(f'{GET_USER_INFO_LINK}?id={user.id}&server_id={ctx.channel.guild.id}')
        data = req.json()
        embed = discord.Embed(title = data['name'])
        for i in range(0, len(data)):
            if list(data.values())[i] == 'id' or list(data.values())[i] == 'serverId':
                continue

            embed.add_field(name=f'{list(data.keys())[i]}:', value=f'{list(data.values())[i]}', inline=False)
        await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == self.server_guild_id:
            welcome_cnl = self.bot.get_channel(self.welcome_cnl_id) 
            infromation_cnl = self.bot.get_channel(self.infromation_cnl_id)
            introduction_cnl = self.bot.get_channel(self.introduction_cnl_id)
            msg = f"Welcome to `server.name` {member.mention}!\nPlease refer to {infromation_cnl.mention} for all you need to know and use command `>introduce` to introduce yourself in {introduction_cnl.mention}"
            await welcome_cnl.send(msg)
        elif member.guild.id == self.tit:
            msg = f"Welcome to `{member.guild.name}` {member.mention}!\n.We hope you enjoy your time here. You can use command `>introduce` to introduce yourself"
            await member.add_roles(member.guild.get_role(int(os.environ["TIT_MEMBER_ROLE"])))
            await self.bot.get_channel(self.tit_main).send(msg)

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
        await user.kick(reason=reason)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit, messages_of: discord.Member = None):
        if messages_of is None:
            deleted = await ctx.channel.purge(limit=int(limit))
        else:
            def check(m):
                return m.author == messages_of
            
            deleted = await ctx.channel.purge(limit=int(limit), check=check)
        
        deleted_of = set()
        for message in deleted:
            deleted_of.add(message.author.name)
        
        await ctx.send(f'Deleted {len(deleted)} message(s) by {deleted_of}')
        await ctx.message.delete(delay=2)

    @commands.command()
    async def roles(self, ctx):
        await ctx.channel.trigger_typing()
        req = requests.get(f'{GET_SERVER_SELFASSIGN_ROLES_LINK}?id={ctx.channel.guild.id}')
        data = req.json()
        out = ''
        index = 1
        for i in data:
            out += f"{index}. {i['role_name']}"
            index += 1
        embed = discord.Embed(title="Self assignable roles", description=out)        
        await ctx.send(embed=embed)

    @commands.command()
    async def assignrole(self, ctx, role_name):
        await ctx.channel.trigger_typing()
        req = requests.get(f'{GET_ID_SELFASSIGN_LINK}?server_id={ctx.channel.guild.id}&role_name={role_name}')
        data = req.json()
        role_id = data['role_id']
        role = ctx.channel.guild.get_role(int(role_id))
        await ctx.message.author.add_roles(role)
        await ctx.send(f"Assigned role: {role.name} to {ctx.author.name}")

def setup(bot):
    bot.add_cog(ServerManagement(bot))