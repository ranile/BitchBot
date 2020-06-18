import discord
from discord.ext import commands as dpy_commands
import jishaku
from jishaku.codeblocks import codeblock_converter
from jishaku.cog import JishakuBase
from jishaku.flags import JISHAKU_HIDE
from jishaku.metacog import GroupCogMeta
from jishaku.modules import package_version
import util
import psutil
import humanize
import sys

from BitchBot import BitchBot
from util import commands


def stats_embed(bot):
    sp = util.space
    proc = psutil.Process()
    self = bot.get_cog('Jishaku')

    with proc.oneshot():
        mem = proc.memory_full_info()

        return discord.Embed(
            color=util.random_discord_color(),
            description=f'**Discord.py version**: `{package_version("discord.py")}`\n'
                        f'**Python version**: `{sys.version}`\n'
                        f'**Jishaku version**: `{jishaku.__version__}`\n'
                        f'**Platform**: `{sys.platform}`\n'
                        f'**Bot load time**: {humanize.naturaltime(self.load_time)}\n'
                        f'**Jishaku cog load time**: {humanize.naturaltime(self.start_time)}\n'
                        '**Memory usage**:\n'
                        f'{sp(4)}**Physical**: {humanize.naturalsize(mem.rss)}\n'
                        f'{sp(4)}**Virtual**: {humanize.naturalsize(mem.vms)} ({humanize.naturalsize(mem.uss)})\n'
                        '**Process**:\n'
                        f'{sp(4)}**PID**: {proc.pid}\n'
                        f'{sp(4)}**Name**: {proc.name()}\n'
                        f'{sp(4)}**Threads in use**: {proc.num_threads()}\n'
                        f'**Guilds count**: {len(bot.guilds)}\n'
                        f'**Unique users**: {len(bot.users)}\n'
                        f'**Channels**: {len(list(bot.get_all_channels()))}\n'
                        f'**Websocket latency**: {round(bot.latency * 1000, 2)}ms'
        )


@commands.group(name="jishaku", aliases=["jsk", "sudo"], hidden=JISHAKU_HIDE,
                invoke_without_command=True, ignore_extra=False)
async def sudo(self, ctx):
    embed = stats_embed(self.bot)
    await ctx.send(embed=embed)


class MyJishaku(JishakuBase, metaclass=GroupCogMeta, command_parent=sudo, name='Jishaku'):
    def __init__(self, bot: BitchBot):
        super().__init__(bot)
        self.bot: BitchBot = bot

    @commands.command(name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Direct evaluation of Python code.
        """

        if '.delete(' in ctx.message.content:
            msg = "Bruh... You don't trust yourself with `.delete(` in an eval"
            await ctx.send(msg)
            raise dpy_commands.BadArgument(msg)
        await super().jsk_python.callback(self, ctx, argument=argument)

    @commands.command(name="shutdown", aliases=["logout", "exit"])
    async def jsk_shutdown(self, ctx: commands.Context):
        """
        Logs this bot out.
        """

        await ctx.send("Exiting...")
        await self.bot.close()

    @commands.command(name="git", aliases=['girl'])
    async def jsk_git(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Shortcut for 'jsk sh git'. Invokes the system shell.
        """

        return await super().jsk_git(ctx, argument=argument)

    @commands.command()
    async def delete(self, ctx, message: discord.Message):
        await message.delete()

    @commands.group(invoke_without_command=True)
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
        except:
            self.bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK} Reloaded cog {cog}')

    @reload.command(name='timers')
    async def reload_timers(self, ctx):
        # noinspection PyUnresolvedReferences
        # loaded with util.timers
        self.bot.timers.restart()
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK} Reloaded Timers')

    @reload.command(name='prefix')
    async def reload_prefixes(self, ctx):
        await self.bot.refresh_prefixes(ctx.db)
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK}')

    @commands.command(aliases=['blacklist'], wants_db=True)
    async def block(self, ctx, user: discord.User, *, reason=None):
        await self.bot.blacklist_user(ctx.db, user, reason=reason)
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK}')

    @commands.command(wants_db=True)
    async def unblock(self, ctx, user: discord.User):
        await self.bot.remove_from_blacklist(ctx.db, user)
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK}')


def setup(bot):
    bot.add_cog(MyJishaku(bot))
