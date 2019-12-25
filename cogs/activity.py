from discord.ext import commands


class Activity(commands.Cog, name='Activity Tracking'):
    """Tracks your activity in the guild and give them activity points for being active.
    With the end goal being the ability to spend these points on a virtual store
    Currently a WIP
    TODOs (for now):
    • TODO: Implement basic tracking of user's activity
    • TODO: Allow users to see their activity
    • TODO: Allow users to see top users in a guild
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Track activity here
        pass

    @commands.group(invoke_without_command=True)
    async def activity(self, ctx):
        await ctx.send('Stub!')

    @activity.command(name='top')
    async def top_users(self, ctx):
        await ctx.send('Stub!')


def setup(bot):
    bot.add_cog(Activity(bot))
