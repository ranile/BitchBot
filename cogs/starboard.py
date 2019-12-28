import discord
from discord.ext import commands

from resources.guild_config import GuildConfig
from services import StarboardService
from services import ConfigService
from util import funs, checks

STAR = '\N{WHITE MEDIUM STAR}'


class Starboard(commands.Cog):
    """A starboard.
    Allow users to star a message.
    Once a message reaches a certain number of stars, it is sent to the starboard channel and saved into the database
    TODOs:
    • Implement basic starboard functionality - Done
    • Save stared messages to database - Done
    • TODO: Allow users to see their star stats
    • TODO: Allow users to see top users who gets stared in a guild
    • TODO: Allow users to pull up a stared message by using the id
    """

    def __init__(self, bot):
        self.bot = bot
        self.already_starred = []
        # star_config = self.bot.get_cog('Config').get_command('config').get_command('starboard')
        star_config = self.bot.get_command('config starboard')
        star_config.add_command(self.setup)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if str(reaction) != STAR:
            return

        if reaction.count >= 2 and reaction.message.id not in self.already_starred and not reaction.message.author.bot:
            config = await ConfigService.get(reaction.message.guild.id)
            if config.starboard_channel is None:
                return

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

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if str(reaction) != STAR:
            return

        config = await ConfigService.get(reaction.message.guild.id)
        if config.starboard_channel is None:
            return

        await StarboardService.unstar(reaction)

    @commands.group(invoke_without_command=True)
    async def star(self, ctx, message):
        star = await StarboardService.get(message, ctx.guild.id)

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

    @star.group(invoke_without_command=True, hidden=True)
    async def stats(self, ctx):
        # Author's star stats
        await ctx.send('Stub!')

    @stats.command(name='top', hidden=True)
    async def top_stared(self, ctx):
        # Guild's star stats
        await ctx.send('Stub!')

    @commands.command()
    @checks.can_config()
    async def setup(self, ctx, channel: discord.TextChannel):
        config = GuildConfig(
            guild_id=ctx.guild.id,
            starboard_channel=channel.id
        )
        inserted = await ConfigService.insert(config)

        await ctx.send(f'Inserted {self.bot.get_channel(inserted.starboard_channel).mention} as starboard channel')


def setup(bot):
    bot.add_cog(Starboard(bot))
