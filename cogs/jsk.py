import discord
from discord.ext import commands
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

    @commands.command(name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Direct evaluation of Python code.
        """

        if '.delete(' in ctx.message.content:
            msg = "Bruh... You don't trust yourself with `.delete(` in an eval"
            await ctx.send(msg)
            raise commands.BadArgument(msg)
        await super().jsk_python.callback(self, ctx, argument=argument)

    @commands.command(name="shutdown", aliases=["logout", "exit"])
    async def jsk_shutdown(self, ctx: commands.Context):
        """
        Logs this bot out.
        """

        await ctx.send("Exiting...")
        await self.bot.close()


def setup(bot):
    bot.add_cog(MyJishaku(bot))
