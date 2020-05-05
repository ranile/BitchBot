import logging

import discord
from discord.ext import commands

from services import StarboardService
from services import ConfigService
from util import funs, checks

log = logging.getLogger('BitchBot' + __name__)
STAR = '\N{WHITE MEDIUM STAR}'


# noinspection PyIncorrectDocstring
class Starboard(commands.Cog):
    """A starboard.
    Allow users to star a message.
    Once a message reaches a certain number of stars, it is sent to the starboard channel and saved into the database
    """

    def __init__(self, bot):
        self.config_service = ConfigService(bot.db)
        self.bot = bot
        self.already_starred = []
        self.starboard_service = StarboardService(bot.db)

    def cog_check(self, ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage("Starboard can't be used in DMs")
        return True

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction) != STAR:
            return

        if user.bot:
            return

        msg = reaction.message

        config = await self.config_service.get(msg.guild.id)
        if config is None or config.starboard_channel is None:
            return

        above_limit, starred = await self.starboard_service.star(reaction)

        if above_limit and msg.id not in self.already_starred:
            author = msg.author

            embed = discord.Embed(
                color=funs.random_discord_color(),
                description=f'**Channel**:{msg.channel.mention}\n\n'
                            f'{starred.message_content}')

            embed.set_author(name=author.display_name, icon_url=author.avatar_url)
            embed.description = starred.message_content
            embed.add_field(name='Original', value=f'[Link]({reaction.message.jump_url})')
            if starred.attachment:
                embed.set_image(url=starred.attachment)
            embed.timestamp = starred.started_at
            self.already_starred.append(msg.id)

            await msg.guild.get_channel(config.starboard_channel).send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if str(reaction) != STAR:
            return

        if user.bot:
            return

        config = await self.config_service.get(reaction.message.guild.id)
        if config is None or config.starboard_channel is None:
            log.debug(f'Skipping starboard star remove for {reaction.message.id} in {reaction.message.guild.id}')
            return

        await self.starboard_service.unstar(reaction)

    @commands.group(invoke_without_command=True)
    async def starboard(self, ctx, message):
        """
        Shows a message from starboard

        Args:
             message: The message ID of the message you wanna pull from starboard
        """
        star = await self.starboard_service.get(message, ctx.guild.id)

        if star is None:
            return await ctx.send('Not found')

        message = await ctx.guild.get_channel(star.channel).fetch_message(star.message_id)
        embed = discord.Embed(color=funs.random_discord_color())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        embed.description = star.message_content
        embed.add_field(name='Original', value=f'[Link]({message.jump_url})')
        if star.attachment:
            embed.set_image(url=star.attachment)
        embed.set_footer(text='Starred at')
        embed.timestamp = star.started_at

        await ctx.send(embed=embed)

    @starboard.group(invoke_without_command=True)
    async def stats(self, ctx):
        """Top 10 people whose messages are starred in a server"""

        top = await self.starboard_service.guild_top_stats(ctx.guild)
        paginator = commands.Paginator(prefix='```md')
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
        me = await self.starboard_service.my_stats(ctx)
        paginator.add_line(f'You: {me["count"]}')

        for page in paginator.pages:
            await ctx.send(page)

    @starboard.command()
    @checks.can_config()
    async def setup(self, ctx, channel: discord.TextChannel, limit=2):
        """
        Setup starboard

        Args:
            channel: The channel you want to use for starboard
            limit: The number of stars required to put a message on the starboard
        """
        inserted = await self.config_service.setup_starboard(ctx.guild.id, channel.id, limit)

        await ctx.send(f'Inserted {self.bot.get_channel(inserted.starboard_channel).mention} as starboard channel')

    @starboard.command()
    @checks.can_config()
    async def delete(self, ctx):
        """Deletes the current starboard config
        The starboard channel along with all of its messages is **not** deleted
        """

        deleted = await self.config_service.delete_starboard(ctx.guild.id)
        if deleted is None:
            return await ctx.send('This server was never configured')
        await ctx.send('Starboard deleted')


def setup(bot):
    bot.add_cog(Starboard(bot))
