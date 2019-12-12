from discord.ext import commands
import discord
import inspect


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def delete(self, ctx, message):
        msg = await ctx.channel.fetch_message(message)
        await msg.delete()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit, messages_of: discord.Member = None):
        if messages_of is None:
            deleted = await ctx.channel.purge(limit=int(limit))
        else:
            def check(m):
                return m.author == messages_of
            
            deleted = await ctx.channel.purge(limit=int(limit), check=check)
        
        deleted_of = set()
        for message in deleted:
            deleted_of.add(message.author.name)
        
        await ctx.send(f'Deleted {len(deleted)} message(s) by {deleted_of}', delete_after = 5)
        await ctx.message.delete(delay=2)

    @commands.command(aliases=["code", "eval"])
    @commands.is_owner()
    async def run(self, ctx, *, code):
        """
        `eval()`s python code
        """

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'commands': commands,
            'discord': discord,
            'guild': ctx.message.guild,
        }

        env.update(globals())

        while str(code).startswith('`'):
            code = str(code)[1:]
        
        while str(code).endswith('`'):
            code = str(code)[:-1]

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            errorOut = f"""```python
            >>> {code}

            {type(e).__name__}:{str(e)}
            ```
            """
            await ctx.send(inspect.cleandoc(errorOut))
            return

        output = f"""```python
        >>> {code}

        {result}
        ```
        """
        await ctx.send(inspect.cleandoc(output))

    @run.error
    async def run_error(self, ctx, error):
        await ctx.send(str(error))

    @commands.command()
    @commands.is_owner()
    async def exit(self, ctx):
        """Kill the bot
        """

        await self.bot.close()

def setup(bot):
    bot.add_cog(Admin(bot))
