import discord
from discord.ext import commands

import keys
from services import EmojiService
from util import funs, BloodyMenuPages, EmbedPagesData


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def arg_or_1(arg: str):
    return int(arg) if arg.isdigit() else 1


# noinspection PyIncorrectDocstring
class Emojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.safe_emojis = []
        self.emoji_service = EmojiService(bot.db)

        self.bot.loop.create_task(self.fetch_safe_emojis())

    async def fetch_safe_emojis(self):
        self.safe_emojis = await self.emoji_service.fetch_all_safe_emojis()

    def safe_emoji_check(self, ctx):
        return (ctx.guild is not None and ctx.guild.id in keys.trusted_guilds) or ctx.author == self.bot.owner_id

    def ensure_safe_emojis(self, ctx, emojis):
        safe_check = self.safe_emoji_check(ctx)
        for emoji in emojis:
            if (emoji.id not in self.safe_emojis and not safe_check) or ctx.channel.is_nsfw():
                raise commands.CheckFailure(
                    f"Channel '{ctx.channel}' needs to be NSFW in order to use emoji '{emoji.name}'.")

    @commands.group(aliases=["e"], invoke_without_command=True)
    async def emoji(self, ctx, emojis: commands.Greedy[discord.Emoji], amount: arg_or_1 = 1):
        """Send any number of the emoji given by 'emojis'

        Only emojis that has been marked safe by bot admins can be used in non-NSFW channels.
        This is a safety feature so that the bot does not send any NSFW content on non-NSFW channels

        Args:
            emojis: The emojis to send.
            amount: The number of times to repeat
        """
        self.ensure_safe_emojis(ctx, emojis)
        to_be_sent = ' '.join([f'{emoji} ' * amount for emoji in emojis])
        if to_be_sent == '':
            return await ctx.send('No emojis of that name found', delete_after=2)
        await ctx.send(to_be_sent)
        await ctx.message.delete(delay=2)

    @emoji.command(aliases=["emojiurl", "l"])
    async def link(self, ctx, emoji: discord.Emoji):
        """Send link of any one of the emoji given by 'emojis' command

        Only emojis that has been marked safe by bot admins can be used in non-NSFW channels.
        This is a safety feature so that the bot does not send any NSFW content on non-NSFW channels

        Args:
            emoji: The emoji to link
        """
        self.ensure_safe_emojis(ctx, [emoji])
        await ctx.send(emoji.url)
        await ctx.message.delete(delay=2)

    @emoji.command()
    async def list(self, ctx):
        """
        Shows the emojis that can be sent by 'emoji' command

        Only emojis that has been marked safe by bot admins are shown in non-NSFW channels.
        This is a safety feature so that the bot does not send any NSFW content on non-NSFW channels
        """
        all_emojis = [e for e in self.bot.emojis if (e.available and self.safe_emoji_check(ctx))]
        chunked_emojis = list(chunks(all_emojis, 20))
        count = 1
        data = []
        for emojis in chunked_emojis:
            embed = discord.Embed(title='Available emojis', color=funs.random_discord_color())
            embed.set_footer(text=f'Total: {len(all_emojis)}')
            out = []
            for emoji in emojis:
                out.append(f'{count}. {emoji.name} \t{emoji}')
                count += 1

            embed.description = '\n'.join(out)
            data.append(embed)

        pages = BloodyMenuPages(EmbedPagesData(data))
        await pages.start(ctx)

    @emoji.command(aliases=['em'])
    async def embed(self, ctx, emoji: discord.Emoji):
        """
        Send embed of any one of the emoji given by 'emojis' command

        Only emojis that has been marked safe by bot admins can be used in non-NSFW channels.
        This is a safety feature so that the bot does not send any NSFW content on non-NSFW channels

        Args:
            emoji: The emoji to send in an the embed
        """
        self.ensure_safe_emojis(ctx, [emoji])
        embed = discord.Embed()
        embed.set_image(url=str(emoji.url))
        await ctx.send(embed=embed)
        await ctx.message.delete(delay=2)

    @emoji.command()
    async def react(self, ctx, message: discord.Message, emoji: discord.Emoji):
        """Make the bot react to a message with the given emoji

        Only emojis that has been marked safe by bot admins can be used in non-NSFW channels.
        This is a safety feature so that the bot does not send any NSFW content on non-NSFW channels

        Arg:
            message: The message to react to
            emoji: The emoji to react with
        """
        self.ensure_safe_emojis(ctx, [emoji])
        await message.add_reaction(emoji)

    @emoji.command(aliases=['marksafe', 'ms'])
    @commands.check(lambda ctx: ctx.author.id in keys.can_use_private_commands)
    async def mark_safe(self, ctx, emoji: discord.Emoji):
        await self.emoji_service.mark_safe(emoji.id, ctx.author.id)
        await self.fetch_safe_emojis()
        await ctx.send(f'\N{WHITE HEAVY CHECK MARK}')


def setup(bot):
    bot.add_cog(Emojis(bot))
