from discord.ext import commands
import discord, requests, json
from keys import (SAVE_USER_INFO_LINK, GET_USER_INFO_LINK,
    GET_SERVER_SELFASSIGN_ROLES_LINK, GET_ID_SELFASSIGN_LINK,
    USER_ROLE, WARN, WARNINGS
)
from ids import  SERVER_GUILD_ID, INFORMATION_CHANNEL_ID, INTRODUCTION_CHANNEL_ID, WELCOME_CHANNEL_ID, INTRO_QUESTIONS

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.intro_result = {}

    @commands.command()
    async def introduce(self, ctx):
        """
        Asks user for their introduction
        """
        # if ctx.channel.guild.id != SERVER_GUILD_ID:
        #     return
        
        if ctx.channel.guild.id == SERVER_GUILD_ID and ctx.channel.id != INTRODUCTION_CHANNEL_ID:
            await ctx.send(f'Wrong channel. Run this command in {self.bot.get_channel(INTRODUCTION_CHANNEL_ID).mention}')
            return

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        intro_result = {}
        intro_result['id'] = str(ctx.author.id)
        intro_result['serverId'] = str(ctx.channel.guild.id)
        for tag, question in INTRO_QUESTIONS.items():
            await ctx.send(question)
            msg = await self.bot.wait_for('message', check=pred)
            intro_result[tag] = msg.content

        requests.post(SAVE_USER_INFO_LINK, json = intro_result)
        if ctx.channel.guild.id == SERVER_GUILD_ID:
            await ctx.message.author.add_roles(ctx.channel.guild.get_role(USER_ROLE))
        await ctx.send('Welcome! Introduction completed')
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
        if member.guild.id == SERVER_GUILD_ID:
            welcome_cnl = self.bot.get_channel(WELCOME_CHANNEL_ID) 
            infromation_cnl = self.bot.get_channel(INFORMATION_CHANNEL_ID)
            introduction_cnl = self.bot.get_channel(INTRODUCTION_CHANNEL_ID)
            msg = f"Welcome to `server.name` {member.mention}!\nPlease refer to {infromation_cnl.mention} for all you need to know and use command `>introduce` to introduce yourself in {introduction_cnl.mention}"
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

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        """
        Ban a user
        Reason is optional. It will show up on the audit log and will be dmed to the banned user
        """
        embed = discord.Embed(title="You have been banned from {}".format(ctx.guild.name), description=reason)
        embed.set_footer(text="Ban by " + ctx.author.display_name)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await user.ban(reason=reason)
        await ctx.send(f"**User {user.mention} has been banned by {ctx.author.mention}**")
        await user.send(embed=embed)
 
 
 
    @commands.command()
    async def warn(self, ctx, user: discord.Member, *, reason):
        warning = {
            'server_id': str(ctx.guild.id),
            'user_id': str(user.id),
            'reason': str(reason),
            'warning_by': str('ctx.author.name')
        }
        requests.post(WARN, json= warning)
        embed = discord.Embed(title=f"{user.name} have been warned by {ctx.author.name} in {ctx.guild.name}", description=reason)
        await ctx.send(embed=embed)
        await user.send(embed=embed)

    @commands.command()
    async def warnings(self, ctx, user: discord.Member):
        req = requests.get(f'{WARNINGS}?server_id={ctx.guild.id}&user_id={user.id}')
        data = req.json()
        embed = discord.Embed(title=f"Warinings for {user.name}")

        for i in data:
            embed.add_field(name = f"{i['reason']}", value=f"Warned by: name", inline=False)

        await ctx.send(embed=embed)
        await user.send(embed=embed)


def setup(bot):
    bot.add_cog(ServerManagement(bot))