import discord
from discord.ext import commands
from datetime import datetime

from resources import Ban, Warn, Mute
from services import MuteService, WarningsService
from services.ban_service import BanService
from services.config_service import GuildConfigService
from util import funs, checks, paginator


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
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(embed=embed)
        # await victim.kick(reason=reason)

        try:
            embed.title = f"You have been Kicked from {ctx.guild.name}"
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't dm that user. Kicked without notice")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, victim: discord.Member, *, reason=None):
        """Ban a user
        """

        if victim.id == ctx.author.id:
            await ctx.send("Why do want to ban yourself?\nI'm not gonna let you do it")
            return

        # await victim.ban(reason=reason)

        ban = Ban(
            reason=reason if reason else None,
            banned_by_id=ctx.author.id,
            banned_user_id=victim.id,
            guild_id=ctx.guild.id,
        )

        saved = await BanService.insert(ban)

        embed = discord.Embed(title=f"User was banned from {ctx.guild.name}", color=funs.random_discord_color(),
                              timestamp=saved.banned_at)
        embed.add_field(name='Banned By', value=ctx.author.mention, inline=True)
        embed.add_field(name='Banned user', value=victim.mention, inline=True)
        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(f'ID: {saved.id}', embed=embed)

        try:
            embed.title = f"You have been banned from {ctx.guild.name}"
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Banned without notice")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def mute(self, ctx: commands.Context, victim: discord.Member, *, reason=None):
        """Mute a user
        """
        await ctx.trigger_typing()

        if victim.id == ctx.author.id:
            await ctx.send("Why do want to mute yourself?\nI'm not gonna let you do it")
            return

        config = await GuildConfigService.get(ctx.guild.id)
        muted = ctx.guild.get_role(config.muted_role_id)

        if muted in victim.roles:
            await ctx.send('User is already muted')
            return

        mute = Mute(
            reason=reason,
            muted_by_id=ctx.author.id,
            muted_user_id=victim.id,
            guild_id=ctx.guild.id
        )
        inserted = await MuteService.insert(mute)

        await victim.add_roles(muted)
        await ctx.send(f"**User {victim.mention} has been muted by {ctx.author.mention}**\nID: {inserted.id}")

        try:
            msg = f"You have been muted in {ctx.guild.name}"
            if reason:
                msg += f" for `{reason}`"

            await ctx.send(msg)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Muted without notice")

    @commands.command()
    @commands.has_permissions(manage_roles=True, manage_channels=True)
    async def unmute(self, ctx: commands.Context, victim: discord.Member):
        """Unmute a user
        """

        await ctx.trigger_typing()
        config = await GuildConfigService.get(ctx.guild.id)
        muted = ctx.guild.get_role(config.muted_role_id)
        await victim.remove_roles(muted)
        await MuteService.delete(ctx.guild.id, victim.id)
        await ctx.send(f"**User {victim.mention} has been unmuted by {ctx.author.mention}**")

    @commands.command()
    @checks.is_mod()
    async def warn(self, ctx: commands.Context, victim: discord.Member, reason: str):
        """Warn a user
        """

        warning = Warn(
            reason=reason,
            warned_by_id=ctx.author.id,
            warned_user_id=victim.id,
            guild_id=ctx.guild.id
        )

        inserted = await WarningsService.insert(warning)

        embed = discord.Embed(title=f"User was warned from {ctx.guild.name}", color=funs.random_discord_color(),
                              timestamp=inserted.warned_at)
        embed.add_field(name='Warned By', value=ctx.author.mention, inline=True)
        embed.add_field(name='Warned user', value=victim.mention, inline=True)
        if reason:
            embed.add_field(name='Reason', value=inserted.reason, inline=False)
        embed.set_thumbnail(url=victim.avatar_url)

        await ctx.send(f'ID: {inserted.id}', embed=embed)

        try:
            embed.title = f"You have been warned in {ctx.guild.name}"
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I can't DM that user. Warned without notice")

    @commands.command()
    @checks.is_mod()
    async def warnings(self, ctx: commands.Context, warnings_for: discord.Member = None):
        """Get warnings for a user
        """
        warnings = await WarningsService.get_all(ctx.guild.id, warnings_for.id)
        pages = commands.Paginator(prefix='```md', max_size=1980)
        index = 1
        for warning in warnings:
            member = ctx.guild.get_member(warning.warned_user_id)
            if member is None:
                continue

            line = f"{index}.  {funs.format_human_readable_user(member)}\n" \
                   f"\tReason: {warning.reason}\n" \
                   f"\tWarned at: {warning.warned_at}\n" \
                   f"\tWarned by {funs.format_human_readable_user(ctx.guild.get_member(warning.warned_by_id))}\n"
            pages.add_line(line)
            index += 1

        react_paginator = paginator.Paginator(data=pages.pages, is_embed=False, ctx=ctx)
        await react_paginator.paginate()

    @mute.command(name='config')
    async def mute_config(self, ctx, role: discord.Role):
        await GuildConfigService.update(ctx.guild.id, 'mute_role_id', role.id)
        await ctx.send(f'Inserted {role.mention} as mute role')


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))