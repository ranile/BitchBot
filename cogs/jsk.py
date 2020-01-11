from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from jishaku.cog import JishakuBase, jsk
from jishaku.metacog import GroupCogMeta


class MyJishaku(JishakuBase, metaclass=GroupCogMeta, command_parent=jsk):

    @commands.command(name="py", aliases=["python"])
    async def jsk_python(self, ctx: commands.Context, *, argument: codeblock_converter):
        if '.delete(' in ctx.message.content:
            msg = "Bruh... You don't trust yourself with `.delete(` in an eval"
            await ctx.send(msg)
            raise commands.BadArgument(msg)
        await super().jsk_python.callback(self, ctx, argument=argument)


def setup(bot):
    bot.add_cog(MyJishaku(bot))
