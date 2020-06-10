import logging
from discord.ext import commands as dpy_commands

from resources import Prefix
from util import checks, commands

logger = logging.getLogger('BitchBot' + __name__)


# noinspection PyIncorrectDocstring
class Config(dpy_commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @dpy_commands.guild_only()
    async def prefix(self, ctx):
        """
        Command group for prefix related command
        Running this command as is will show current prefixes
        """

        await ctx.send(f"Current prefixes are : {self._get_all_prefixes_presentable(ctx)}")

    @prefix.command(name='set', wants_db=True)
    @checks.can_config()
    @dpy_commands.guild_only()
    async def set_prefix(self, ctx, prefix):
        """
        Add a prefix for this server
        The prefix length must be less than 6.
        If the prefix contains spaces, it must be enclosed in braces

        You need `Manage Server` permissions to run this command

        Args:
            prefix: The prefix to add
        """

        if len(prefix) > 6:
            raise dpy_commands.BadArgument(f"Prefix length must be less than 6, not {len(prefix)}")
        added = await self.bot.set_prefix(ctx.db, Prefix(guild_id=ctx.guild.id, prefix=prefix))
        await ctx.send(f'Set prefix: `{added}`\n'
                       f'Current prefixes are : {self._get_all_prefixes_presentable(ctx)}')

    @prefix.command(name='remove', aliases=['clear'])
    @checks.can_config()
    @dpy_commands.guild_only()
    async def remove_prefix(self, ctx):
        """
        Removes the server's custom prefix.
        Once custom prefix is removed, `>` will be the prefix along with @ mention.

        You need `Manage Server` permissions to run this command
        """

        await self.bot.clear_custom_prefix(ctx.db, ctx.guild.id)
        await ctx.send(f'Successfully cleared custom prefix\n'
                       f'Current prefixes are : {self._get_all_prefixes_presentable(ctx)}')

    def _get_all_prefixes_presentable(self, ctx):
        prefixes = [ctx.me.mention]
        try:
            prefixes.append(f'`{self.bot.prefixes[ctx.guild.id]}`')
        except KeyError:
            prefixes.append('`>`')

        return ', '.join(prefixes)


def setup(bot):
    bot.add_cog(Config(bot))
