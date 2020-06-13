import re
import typing
from typing import Union

import discord
from discord.ext import commands as dpy_commands

import util
from BitchBot import BitchBot
from util import converters, checks, commands


def c_to_f(c: float) -> float:
    return (c * 9 / 5) + 32


def f_to_c(f: float) -> float:
    return (f - 32) * (5 / 9)


# noinspection SpellCheckingInspection,PyPep8Naming,PyIncorrectDocstring
class Miscellaneous(dpy_commands.Cog):
    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot

    @commands.command(aliases=["send"], hidden=True)
    @checks.owner_only_in_non_trusted_guilds()
    async def say(self, ctx: commands.Context, *, message: str):
        """Have the bot say something.

        This command can only be used bot admins

        Args:
            message: The message you want to say
        """

        await ctx.channel.trigger_typing()
        sentMessage = await ctx.send(message)
        await util.log(ctx, message, sentMessage)
        await ctx.message.delete(delay=5)

    @commands.command(aliases=["addreaction"], hidden=True)
    @checks.owner_only_in_non_trusted_guilds()
    async def react(self, ctx: commands.Context, msg: discord.Message, text: str):
        """
        Add the given reactions to a message

        This command can only be used bot admins

        Args:
            msg: The message you want to react to
            text: The letter reactions you want to add
        """

        sent = []
        for i in text:
            if re.fullmatch(r'[a-z]', i, re.IGNORECASE):
                await msg.add_reaction(util.EMOJI_CHARS[str(i).lower()])
                sent.append(i)

        await util.log(ctx, text, ctx.message, ''.join(sent))

    @commands.command(aliases=["yell"], hidden=True)
    @checks.owner_only_in_non_trusted_guilds()
    async def touppercase(self, ctx: commands.Context, *, msg: str):
        """
        Convert string to upper case

        This command can only be used bot admins

        Args:
            msg: Message you want in upper case
        """
        out = str(msg).upper()
        sentMessage = await ctx.send(out)
        await util.log(ctx, msg, sentMessage, out)
        await ctx.message.delete()

    @commands.command(aliases=["to_c"])
    async def toc(self, ctx: commands.Context, *, temp: float):
        """
        Convert fahrenheit to celsius.
        Example: '>toc 69'.

        Args:
            temp: temperature in celsius
        """

        await ctx.send(f'{int(f_to_c(temp))}°C')

    @commands.command(aliases=["to_f"])
    async def tof(self, ctx: commands.Context, temp: float):
        """
        Convert celsius to fahrenheit.
        Example: '>tof 20.5'.

        Args:
            temp: temperature in fahrenheit
        """

        await ctx.send(f'{int(c_to_f(temp))}°F')

    @commands.command()
    async def poll(self, ctx: commands.Context, question: str, *answers: typing.Tuple[str]):
        """
        Start a poll.
        If answers/questions contain spaces put it in quotes
        Example:
            >poll "Do you like bacon" yes

        Args:
            question: The question you want to ask. This will be title of embed
            answers: The answers for the poll. If omitted, it will default to yes/no. Max of 10 answers are allowed
        """

        if len(answers) > len(util.EMOJI_CHARS):
            raise dpy_commands.BadArgument('Answers must be 26 or less')

        desc = []
        letter_emoji = list(util.EMOJI_CHARS.values())

        for i, answer in enumerate(answers):
            desc.append(f'{letter_emoji[i]} {answers[i]}')

        embed = discord.Embed(
            title=f'**📊 {question}**',
            description='\n'.join(desc),
            color=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        ).set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))

        msg = await ctx.send(embed=embed)
        if len(answers) == 0:
            for e in ('\N{THUMBS UP SIGN}', '\N{THUMBS DOWN SIGN}'):
                await msg.add_reaction(e)
        else:
            for i in range(len(desc)):
                await msg.add_reaction(letter_emoji[i])

    @commands.command(aliases=['info', 'binfo'])
    async def about(self, ctx: commands.Context):
        """
        Tells you about me
        """

        # this exists but in a way that ij can't pick it up
        # TODO move it to Bot
        # noinspection PyUnresolvedReferences
        embed = discord.Embed(color=util.random_discord_color(),
                              timestamp=self.bot.get_cog('Jishaku').load_time)
        owner = self.bot.get_user(self.bot.owner_id)
        embed.set_author(name=f"{owner.name}#{owner.discriminator}", icon_url=str(owner.avatar_url))
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.add_field(name="Source", value=f"[GitHub Respositiory](https://github.com/hamza1311/BitchBot)")
        embed.add_field(name='Comamnds', value=f"{len(self.bot.cogs)} Cogs loaded\n{len(self.bot.commands)} commands")
        members = list(self.bot.get_all_members())
        embed.add_field(name='Members', value=f'Total: {len(members)}\nUnique: {len(set(m.id for m in members))}')
        embed.add_field(name='Total web socket events received', value=str(sum(list(self.bot.socket_stats.values()))))
        embed.set_footer(text=f"Written in discord.py v{discord.__version__}. Up Since",
                         icon_url='https://i.imgur.com/RPrw70n.png')

        await ctx.send(embed=embed)

    @commands.command(name='userinfo', aliases=['whois', 'uinfo'])
    async def user_info(self, ctx: commands.Context, member: Union[discord.Member, converters.FetchedUser] = None):
        """
        Shows info about author or a user if provided

        Args:
            member: The user who's info you wanna see
        """
        # TODO Rewrite this command
        user = member or ctx.author

        embed = discord.Embed(color=user.color)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='ID', value=str(user.id))
        embed.add_field(name='Created At', value=str(user.created_at))  # TODO: format time

        # access of member specific props ahead so send the message and return if `user` is not a `Member`
        if not isinstance(user, discord.Member):
            return await ctx.send(embed=embed)

        embed.add_field(name='Joined At', value=str(user.joined_at))  # TODO: format time
        if user.premium_since is not None:
            embed.add_field(name='Last boosted on', value=str(user.premium_since))  # TODO: format time
        # embed.add_field(name='Is on mobile', value=user.is_on_mobile()) TODO think about it
        embed.add_field(name='Permissions', value=util.user_presentable_perms(user.guild_permissions), inline=False)
        sorted_roles = sorted(user.roles[1:], key=lambda x: x.position, reverse=True)
        embed.add_field(name='Roles', value=', '.join([r.mention for r in sorted_roles]), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx: commands.Context):
        """Gives you a link to the source code"""
        await ctx.send(embed=discord.Embed(
            description=f"The {self.bot.lines_of_code_count} lines of actual Python 3 code that "
                        f"I'm made of can be found [here](https://github.com/hamza1311/BitchBot)",
            color=util.random_discord_color()
        ))

    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Invite me to your server"""

        await ctx.send(
            embed=discord.Embed(
                title='Invite Link',
                url='https://discordapp.com/oauth2/authorize?client_id=595363392886145046&scope=bot&permissions=388160',
                color=util.random_discord_color()
            ).add_field(name="Need help? Have any ideas for the bot? Want to report a bug?",
                        value=f"[Join our support server]({util.SUPPORT_SERVER_INVITE})")
            .set_author(name=str(ctx.me), icon_url=ctx.me.avatar_url_as(format='png'))
            .set_footer(text=f'Rquested by {ctx.author.display_name}',
                        icon_url=ctx.author.avatar_url_as(format='png'))
        )

    # noinspection PyUnresolvedReferences
    @commands.command(hidden=True, usage='<time> <other_arg>')
    async def parse(self, ctx: commands.Context, *, time_and_arg: converters.HumanTime(other=True)):
        """
        Parses human time friendly time

        Example:
            `{prefix}parse 1 hour This is a test`
            where `1 hour` is time and `This is a test` is the other arg

        Args:
            time: The time to parse
            arg: The argument you want to pass
        """
        import pendulum
        async with ctx.typing():
            time = pendulum.instance(time_and_arg.time)
            await ctx.send(f'Time: {repr(time)}\n'
                           f'Other argument: {time_and_arg.other}\n'
                           f'Delta: {(time - pendulum.instance(ctx.message.created_at)).in_words()}')


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
