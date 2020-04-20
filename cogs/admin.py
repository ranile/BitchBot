import importlib
import logging

from discord.ext import commands
import sys
import re

from util import funs

_GIT_PULL_REGEX = re.compile(r'\s+(?P<filename>.+?)\s*\|\s*[0-9]+\s*[+-]+')

log = logging.getLogger('BitchBot' + __name__)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def delete(self, ctx, message):
        msg = await ctx.channel.fetch_message(message)
        await msg.delete()

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog):
        """
        Reloads a cog

        Args:
            cog: The cog to reload
        """
        try:
            actual_cog = self.bot.get_cog(cog)
            name = actual_cog.__class__.__module__
            self.bot.reload_extension(name)
            log.info(f'Reloaded cog: {actual_cog.qualified_name} ({name})')
        except:
            self.bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK} Reloaded cog {cog}')

    @reload.command(name='all')
    @commands.is_owner()
    async def reload_all(self, ctx):
        stdout, stderr = await funs.run_shell_command('git pull')
        files = _GIT_PULL_REGEX.findall(stdout)

        all_modules = 0
        successfully_reloaded_modules = 0
        for file in files:
            if file == 'core.py':  # core.py has changed so return and prompt the user to reload the bot completely
                return await ctx.send('`core.py` changed.\nReload the bot completely.\nExiting')

            # Only reload the python files that are not in cogs directory (aren't cogs)
            if not file.startswith('cogs/') and file.endswith('.py'):
                all_modules += 1
                try:
                    module = sys.modules[file[:-3].replace('/', '.')]
                    importlib.reload(module)
                    successfully_reloaded_modules += 1
                    log.info(f'Reloaded module: {module.__name__}')
                except Exception as e:
                    log.error(e)

        # Reload all the cogs instead of figuring out which cogs used the updated modules and only reloading those
        # Maybe that's for another day
        all_cogs = len(self.bot.cogs)
        successfully_reloaded_cogs = 0
        for _, cog in self.bot.cogs.items():
            name = cog.__class__.__module__
            try:
                self.bot.reload_extension(name)
                successfully_reloaded_cogs += 1
                log.info(f'Reloaded cog: {cog.qualified_name}')
            except Exception as e:
                log.error(e)

        await ctx.send(f"Successfully reloaded {successfully_reloaded_modules}/{all_modules} modules "
                       f"and {successfully_reloaded_cogs}/{all_cogs} cogs")

    @reload.command(name='timers')
    @commands.is_owner()
    async def reload_timers(self, ctx):
        self.bot.timers.restart()
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK} Reloaded Timers')

    @reload.command(name='prefix')
    @commands.is_owner()
    async def reload_prefixes(self, ctx):
        await self.bot.refresh_prefixes()
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK}')


def setup(bot):
    bot.add_cog(Admin(bot))
