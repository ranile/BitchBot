import logging

import discord
import typing
from discord.ext import commands as dpy_commands

from BitchBot import BitchBot
from services import StarboardService
from services import ConfigService
from util import funs, checks, commands

log = logging.getLogger('BitchBot' + __name__)
STAR = '\N{WHITE MEDIUM STAR}'
# TODO: Redo everything


# noinspection PyIncorrectDocstring
class Starboard(dpy_commands.Cog):
    """A starboard.
    Allow users to star a message.
    Once a message reaches a certain number of stars, it is sent to the starboard channel and saved into the database
    """

    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot
        self.already_starred = []

    async def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            raise dpy_commands.NoPrivateMessage("Starboard can't be used in DMs")
        if ctx.command.name == self.setup.name:
            return True
        config = await ConfigService.get(ctx.db, ctx.guild.id)
        if config is None or config.starboard_channel is None:
            raise dpy_commands.CommandError('You need starboard enabled')
        return True

    @dpy_commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: typing.Union[discord.Member, discord.User]):
        if str(reaction) != STAR:
            return

        if user.bot:
            return

        msg = reaction.message

        async with self.bot.db.acquire() as db:
            config = await ConfigService.get(db, msg.guild.id)
            if config is None or config.starboard_channel is None:
                return

            above_limit, starred = await StarboardService.star(db, reaction)

        if above_limit and msg.id not in self.already_starred:
            author = msg.author

            embed = discord.Embed(
                color=funs.random_discord_color(),
                description=f'**Channel**:{msg.channel.mention}\n\n'
                            f'{starred.message_content}')

            embed.set_author(name=author.display_name, icon_url=str(author.avatar_url))
            embed.description = starred.message_content
            embed.add_field(name='Original', value=f'[Link]({reaction.message.jump_url})')
            if starred.attachment:
                embed.set_image(url=starred.attachment)
            embed.timestamp = starred.started_at
            self.already_starred.append(msg.id)

            await msg.guild.get_channel(config.starboard_channel).send(embed=embed)

    @dpy_commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: typing.Union[discord.Member, discord.User]):
        if str(reaction) != STAR:
            return

        if user.bot:
            return
        async with self.bot.db.acquire() as db:
            config = await ConfigService.get(db, reaction.message.guild.id)
            if config is None or config.starboard_channel is None:
                log.debug(f'Skipping starboard star remove for {reaction.message.id} in {reaction.message.guild.id}')
                return

            await StarboardService.unstar(db, reaction)

    @commands.group(invoke_without_command=True, wants_db=True)
    async def starboard(self, ctx: commands.Context, message: int):
        """
        Shows a message from starboard

        Args:
             message: The message ID of the message you wanna pull from starboard
        """
        star = await StarboardService.get(ctx.db, message, ctx.guild.id)

        if star is None:
            return await ctx.send('Not found')

        message = await ctx.guild.get_channel(star.channel).fetch_message(star.message_id)
        embed = discord.Embed(color=funs.random_discord_color())
        embed.set_author(name=message.author.display_name, icon_url=str(message.author.avatar_url))
        embed.description = star.message_content
        embed.add_field(name='Original', value=f'[Link]({message.jump_url})')
        if star.attachment:
            embed.set_image(url=star.attachment)
        embed.set_footer(text='Starred at')
        embed.timestamp = star.started_at

        await ctx.send(embed=embed)

    @starboard.group(invoke_without_command=True, wants_db=True)
    async def stats(self, ctx: commands.Context):
        """Top 10 people whose messages are starred in a server"""

        top = await StarboardService.guild_top_stats(ctx.db, ctx.guild)
        paginator = dpy_commands.Paginator(prefix='```md')
        length = 0
        for starred in top:
            member = starred["author"]
            try:
                line = f'{member.display_name} ({member}): {starred["count"]}'
                paginator.add_line(line)
                if length < len(line):
                    length = len(line)
            except AttributeError:
                pass

        paginator.add_line()
        paginator.add_line('-' * length)
        me = await StarboardService.members_stats(ctx.db, ctx.guild.id, ctx.author.id)
        if me is not None:
            paginator.add_line(f'You: {me["count"]}')
        else:
            paginator.add_line(f'You: None')

        for page in paginator.pages:
            await ctx.send(page)

    @starboard.command(wants_db=True)
    @checks.can_config()
    async def setup(self, ctx: commands.Context, channel: discord.TextChannel, limit: int = 2):
        """
        Setup starboard

        Args:
            channel: The channel you want to use for starboard
            limit: The number of stars required to put a message on the starboard
        """
        inserted = await ConfigService.setup_starboard(ctx.db, ctx.guild.id, channel.id, limit)

        await ctx.send(f'Inserted {self.bot.get_channel(inserted.starboard_channel).mention} as starboard channel')

    @starboard.command(wants_db=True)
    @checks.can_config()
    async def delete(self, ctx: commands.Context):
        """Deletes the current starboard config
        The starboard channel along with all of its messages is **not** deleted
        """

        deleted = await ConfigService.delete_starboard(ctx.db, ctx.guild.id)
        if deleted is None:
            return await ctx.send('This server was never configured')
        await ctx.send('Starboard deleted')


def setup(bot):
    bot.add_cog(Starboard(bot))
