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
    @commands.guild_only()
    async def prefix(self, ctx):
        """
        Command group for prefix related command
        Running this command as is will show current prefixes
        """
        prefixes = []
        for i in self.bot.prefixes[ctx.guild.id]:
            prefixes.append(f'`{i}`')
        await ctx.send(f"Current prefixes are : {', '.join(prefixes)}")

    @prefix.command(name='add')
    @checks.can_config()
    @commands.guild_only()
    async def add_prefix(self, ctx, prefix):
        """
        Add a prefix for this server
        The prefix length must be less than 6.
        If the prefix contains spaces, it must be enclosed in braces

        You need `Manage Server` permissions to run this command

        Args:
            prefix: The prefix to add
        """

        if len(prefix) > 6:
            raise commands.BadArgument(f"Prefix length must be less than 6, not {len(prefix)}")
        added = await self.bot.add_prefix(Prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f'Added prefix: `{added}`')

    @prefix.command(name='remove')
    @checks.can_config()
    @commands.guild_only()
    async def remove_prefix(self, ctx, prefix):
        """
        Removes a prefix

        You need `Manage Server` permissions to run this command

        Args:
            prefix: The prefix to remove
        """

        added = await self.bot.remove_prefix(Prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f'Removed prefix: `{added}`')


def setup(bot):
    bot.add_cog(Config(bot))
