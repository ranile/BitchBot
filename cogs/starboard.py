import discord
from discord.ext import commands

from services import StarboardService
from services import ConfigService
from util import funs

STAR = '\N{WHITE MEDIUM STAR}'


class Starboard(commands.Cog):
    """A starboard.
    Allow users to star a message.
    Once a message reaches a certain number of stars, it is sent to the starboard channel and saved into the database
    TODOs:
    • TODO: Implement basic starboard functionality
    • TODO: Save stared messages to database
    • TODO: Allow users to see their star stats
    • TODO: Allow users to see top users who gets stared in a guild
    • TODO: Allow users to pull up a stared message by using the id

    SQL table:
        ```create table if not exists Starboard
        (
            message_id      bigint    not null,
            id              serial    not null primary key,
            started_at      timestamp not null default now(),
            message_content text,
            attachment      text,
            stars_count     int       not null
        );

        create unique index unique_message on Starboard (message_id);```
    """

    def __init__(self, bot):
        self.bot = bot
        self.already_starred = []

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction) != STAR:
            return

        if reaction.count >= 1 and reaction.message.id not in self.already_starred and not reaction.message.author.bot:
            config = await ConfigService.get(reaction.message.guild.id)
            should_send, starred = await StarboardService.star(reaction)
            if should_send:
                author = reaction.message.author
                embed = discord.Embed(color=funs.random_discord_color())
                embed.set_author(name=author.display_name, icon_url=author.avatar_url)
                embed.description = starred.message_content
                embed.add_field(name='Original', value=f'[Link]({reaction.message.jump_url})')
                if starred.attachment:
                    embed.set_image(url=starred.attachment)
                embed.set_footer(text='Starred at')
                embed.timestamp = starred.started_at
                await reaction.message.guild.get_channel(config.starboard_channel).send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def star(self, ctx, message):
        await ctx.send('Stub!')

    @star.group(invoke_without_command=True)
    async def stats(self, ctx):
        await ctx.send('Stub!')

    @stats.command(name='top')
    async def top_stared(self, ctx):
        await ctx.send('Stub!')


def setup(bot):
    bot.add_cog(Starboard(bot))
