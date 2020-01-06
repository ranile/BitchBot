from datetime import datetime

import discord
from discord.ext import commands

from database import database
from services.config_service import GuildConfigService
from util import funs


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def trigger_webhook(self, webhook_url, content, username, avatar_url=None):
        webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(self.bot.clientSession))
        if isinstance(content, discord.Embed):
            await webhook.send(embed=content, username=username, avatar_url=avatar_url)
        else:
            await webhook.send(content, username=username, avatar_url=avatar_url)

    # noinspection PyMethodMayBeStatic
    def format_human_readable_user(self, user):
        return f'{user.name}#{user.discriminator}'

    def base_member_embed(self, member):
        embed = discord.Embed(timestamp=datetime.utcnow(),
                              color=funs.random_discord_color())
        embed.set_author(name=self.format_human_readable_user(member), icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='User id', value=member.id)
        return embed

    async def send_log(self, name, member=None, embed=None, guild=None):
        if isinstance(member, discord.Member):
            if embed is None:
                # noinspection PyTypeChecker
                embed = self.base_member_embed(member)
            if guild is None:
                guild = member.guild

        config = await GuildConfigService.get(guild.id)
        await self.trigger_webhook(config.event_log_webhook, embed, name)

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        member = ctx.author
        embed = self.base_member_embed(member)
        embed.title = 'A new member joined'
        await self.send_log(member=member, name='on_member_join', embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, ctx):
        member = ctx.author
        embed = self.base_member_embed(member)
        embed.title = 'Member left'
        await self.send_log(member=member, name='on_member_remove', embed=embed)

    # noinspection PyMethodMayBeStatic
    def base_role_embed(self, role):
        embed = discord.Embed(color=funs.random_discord_color(), timestamp=datetime.utcnow())
        embed.add_field(name='Role name', value=role.name)
        embed.add_field(name='Role id', value=role.id)
        return embed

    @commands.Cog.listener()
    async def on_guild_role_create(self, ctx, role: discord.Role):
        embed = self.base_role_embed(role)
        embed.title = 'Role created'
        await self.send_log(name='role_create', embed=embed, guild=role.guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, ctx, role: discord.Role):
        embed = self.base_role_embed(role)
        embed.title = 'Role deleted'
        await self.send_log(name='role_delete', embed=embed, guild=role.guild)

    @commands.Cog.listener()
    async def on_member_ban(self, ctx):
        guild, user = ctx.guild, ctx.author
        embed = self.base_member_embed(user)
        embed.title = "Member banned"
        await self.send_log(name='on_member_ban', guild=guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, ctx):
        guild, user = ctx.guild, ctx.author
        embed = self.base_member_embed(user)
        embed.title = "Member unbanned"
        await self.send_log(name='on_member_unban', guild=guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return

        embed = self.base_member_embed(after)
        diff = set(after.roles) - set(before.roles)
        text = 'Role added'
        if len(diff) == 0:
            diff = set(before.roles) - set(after.roles)
            text = 'Role removed'

        embed.description = repr(diff)
        embed.add_field(name='Operation', value=text)
        print(diff)
        await self.send_log(member=after, name='on_member_update', embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        pass


def setup(bot):
    bot.add_cog(Logging(bot))
