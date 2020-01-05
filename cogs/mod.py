import asyncio
from datetime import datetime, timedelta

import discord
import re
import time
from discord.ext import commands

from services.config_service import GuildConfigService
from util import funs, checks


class Ban:
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.banned_at = kwargs.pop('banned_a')
        self.banned_by_id = kwargs.pop('banned_by_id')
        self.banned_user_id = kwargs.pop('banned_user_id')
        self.unban_time = kwargs.pop('unban_time')


class Mute:
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.muted_at = kwargs.pop('muted_at')
        self.muted_by_id = kwargs.pop('muted_by_id')
        self.muted_user_id = kwargs.pop('muted_user_id')


class Warn:
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.warned_at = kwargs.pop('warned_at')
        self.warned_by_id = kwargs.pop('warned_by_id')
        self.warned_user_id = kwargs.pop('warned_user_id')


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, victim: discord.Member, *, reason: str = None):
        """Yeet a user
        """

        embed = discord.Embed(title=f"User was Kicked from {ctx.guild.name}",
                              color=funs.random_discord_color(),
                              timestamp=datetime.utcnow())
        embed.add_field(name='Kicked By', value=ctx.author.mention, inline=True)
        embed.add_field(name='Kicked user', value=victim.mention, inline=True)
        if reason: embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(embed=embed)
        await victim.kick(reason=reason)

        try:
            embed.title = f"You have been Kicked from {ctx.guild.name}"
            await victim.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't dm that user. Kicked without notice")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, victim: discord.Member, *, reasonAndDuration: str = ""):
        """Ban a user
        """

        if victim.id == ctx.author.id:
            await ctx.send("Why do want to ban yourself?\nI'm not gonna let you do it")
            return

        duration = re.search(f'([0-9]+)? ?', reasonAndDuration).group(0).strip()
        reason = reasonAndDuration[len(duration):].strip()

        await victim.ban(reason=reason)

        ban = Ban(
            reason=reason if reason else None,
            banned_at=datetime.utcnow(),
            banned_by_id=ctx.author.id,
            banned_user_id=victim.id,
            unban_time=(datetime.utcnow() + timedelta(hours=2)),
        )

        embed = discord.Embed(title=f"User was banned from {ctx.guild.name}", color=funs.random_discord_color(),
                              timestamp=datetime.utcnow())
        embed.add_field(name='Banned By', value=ctx.author.mention, inline=True)
        embed.add_field(name='Banned user', value=victim.mention, inline=True)
        embed.add_field(name='Banned till', value='formatTime(ban.unbanTime)', inline=True)
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(embed=embed)

        try:
            embed.title = f"You have been banned from {ctx.guild.name}"
            await victim.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Banned without notice")

        if duration:
            await asyncio.sleep(int(duration))
            await victim.unban()

    @commands.command()
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def mute(self, ctx: commands.Context, victim: discord.Member, *, reasonAndDuration: str = ""):
        """
        Mute a user
        Duration must be given in seconds. Use a calculator, not me.
        Mute will become permanent if bot script is restarted
        """
        await ctx.trigger_typing()

        duration = re.search(f'([0-9]+)? ?', reasonAndDuration).group(0).strip()
        reason = reasonAndDuration[len(duration):].strip()

        if victim.id == ctx.author.id:
            await ctx.send("Why do want to mute yourself?\nI'm not gonna let you do it")
            return

        config = await GuildConfigService.get(ctx.guild.id)
        muted = ctx.guild.get_role(config.muted_role_id)

        if muted in victim.roles:
            await ctx.send('User is already muted')
            return

        out = f"**User {victim.mention} has been muted by {ctx.author.mention}**"

        await victim.add_roles(muted)
        await ctx.send(out)

        try:
            msg = f"You have been muted in {ctx.guild.name}"
            if reason:
                msg += f" for `{reason}`"

            await victim.send(msg)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Muted without notice")

        mute = Mute(
            reason=reason,
            muted_at=int(time.time()),
            muted_by_id=ctx.author.id,
            muted_user_id=victim.id,
        )

        if duration:
            await asyncio.sleep(int(duration))
            await victim.remove_roles(muted)

    @commands.command()
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def unmute(self, ctx: commands.Context, victim: discord.Member):
        """Unmute a user
        """

        await ctx.trigger_typing()
        config = await GuildConfigService.get(ctx.guild.id)
        muted = ctx.guild.get_role(config.muted_role_id)
        await victim.remove_roles(muted)
        await ctx.send(f"**User {victim.mention} has been unmuted by {ctx.author.mention}**")

    @commands.command()
    @checks.is_mod()
    async def warn(self, ctx: commands.Context, victim: discord.Member, reason: str):
        """Warn a user
        """

        warning = Warn(
            reason=reason,
            warned_at=datetime.utcnow(),
            warned_by_id=ctx.author.id,
            warned_user_id=victim.id,
        )

        embed = discord.Embed(title=f"User was Warned from {ctx.guild.name}", color=funs.random_discord_color(),
                              timestamp=warning.warned_at)
        embed.add_field(name='Warned By', value=ctx.author.mention, inline=True)
        embed.add_field(name='Warned user', value=victim.mention, inline=True)
        if reason:
            embed.add_field(name='Reason', value=warning.reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(embed=embed)

        try:
            embed.title = f"You have been Warned in {ctx.guild.name}"
            await victim.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Warned without notice")

    @commands.command()
    @checks.is_mod()
    async def warnings(self, ctx: commands.Context, warnings_for: discord.Member):
        """Get warnings for a user
        """

        warnings = []
        embed = discord.Embed(title=f"Warnings for {warnings_for.name}", color=funs.random_discord_color())
        index = 1
        for warning in warnings:
            embed.add_field(
                name=f"{index}. {warning.reason}",
                value=f"Warned by: {warning.warnedByUsername}\nWarned at",
                inline=False
            )

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
