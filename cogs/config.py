import logging
from discord.ext import commands

from resources import Prefix
from services import ConfigService
from util import checks

logger = logging.getLogger('BitchBot' + __name__)


# noinspection PyIncorrectDocstring
class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_service = ConfigService(bot.db)

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Command group for prefix related command"""
        await ctx.send_help(ctx)

    @prefix.command(name='add')
    @checks.can_config()
    async def add_prefix(self, ctx, prefix):
        """
        Add a prefix for this server
        The prefix length must be less than 6.
        If the prefix contains spaces, it must be enclosed in braces

        Args:
            prefix: The prefix to add
        """

        if len(prefix) > 6:
            raise commands.BadArgument(f"Prefix length must be less than 6, not {len(prefix)}")
        added = await self.bot.add_prefix(Prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f'Added prefix: `{added}`')

    @prefix.command(name='remove')
    @checks.can_config()
    async def remove_prefix(self, ctx, prefix):
        """
        Removes a prefix

        Args:
            prefix: The prefix to remove
        """

        added = await self.bot.remove_prefix(Prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f'Removed prefix: `{added}`')


def setup(bot):
    bot.add_cog(Config(bot))
