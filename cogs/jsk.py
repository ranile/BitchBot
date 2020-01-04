from discord.ext import commands
from jishaku.cog import JishakuBase, jsk
from jishaku.metacog import GroupCogMeta


class MyJishaku(JishakuBase, metaclass=GroupCogMeta, command_parent=jsk):

    async def cog_check(self, ctx: commands.Context):
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You must own this bot to use Jishaku.")

        elif '.delete' in ctx.message.content and ctx.command.name == 'py':
            raise commands.BadArgument("Bruh... You don't trust yourself with `.delete` in an eval")
        return True


def setup(bot):
    bot.add_cog(MyJishaku(bot))
