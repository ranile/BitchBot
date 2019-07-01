from discord.ext import commands
import discord
import asyncio
import re


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        await user.send(embed=embed)
        await ctx.send("**User {} has been banned by {}**".format(user.mention, ctx.author.mention))
        await user.ban(reason=reason)

    @ban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to ban")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions to run that command")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to ban that user")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        """
        Kick a user
        Reason is optional. It will show up on the audit log and will be dmed to the kicked user
        """
        embed = discord.Embed(title="You have been kicked from {}".format(ctx.guild.name), description=reason)
        embed.set_footer(text="Kick by " + ctx.author.display_name)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await user.send(embed=embed)
        await ctx.send("**User {} has been kicked by {}**".format(user.mention, ctx.author.mention))
        await user.kick(reason=reason)

    @kick.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to kick")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions to run that command")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to kick that user")

    @commands.command()
    @commands.has_role("Mod Permissions")
    async def mute(self, ctx, user: discord.Member, *, time_and_reason):
        """
        Stops a user from messaging in all channels.
        Time and reason must be in that order. Both are optional. If not time is specified, the mute will be permanant.
        Use >unmute to remove it
        """
        if re.match(r"(([0-9]+) ?)?(.*)?", time_and_reason):
            match = re.match(r"(([0-9]+) ?)?(.*)?", time_and_reason)
            time = match.group(2)
            reason = match.group(3)
            if not reason:
                reason = None
            if not time:
                time = None
            else:
                time = int(time)
        else:
            raise commands.MissingRequiredArgument
        server_roles = ctx.guild.roles
        server_roles = (x.name for x in server_roles)
        if "Muted" not in server_roles:
            muted = await ctx.guild.create_role(name="Muted")
        else:
            muted = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted = muted[0]

        await user.add_roles(muted)

        await ctx.send("User {} has been muted by {} for '{}'".format(user.mention, ctx.author.mention, reason))

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted, send_messages=False, add_reactions=False)

        if time:
            await asyncio.sleep(time)
            await user.remove_roles(muted)

    @mute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to mute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to mute that user")
        elif isinstance(error, commands.MissingRole):
            await ctx.send("You need to be a moderator to use that command")

    @commands.command()
    @commands.has_role("Mod Permissions")
    async def unmute(self, ctx, user:discord.Member):
        """
        Removes the mute from the specified user
        """
        muted = [x for x in ctx.guild.roles if x.name == "Muted"]
        muted = muted[0]
        await user.remove_roles(muted)
        await ctx.send("User {} has been unmuted by {}".format(user.mention, ctx.author.mention))

    @unmute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to mute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to mute that user")
        elif isinstance(error, commands.MissingRole):
            await ctx.send("You need to be a moderator to use that command")

    @commands.command()
    async def purge(self, ctx, amount: int):
        """
        Delete many messages in a row
        """
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send("{} has deleted {} messages".format(ctx.author.mention, amount), delete_after=7)
        else:
            await ctx.send("You don't have permissions to delete messages in this channel")


def setup(bot):
    bot.add_cog(Moderation(bot))
