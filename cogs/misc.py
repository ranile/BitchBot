from typing import Union

import aiohttp
import asyncio
import discord
import re
import string
from discord.ext import commands
import dialogflow_v2 as dialogflow
import git
from TextToOwO.owo import text_to_owo
from datetime import datetime
from keys import logWebhook, project_id
from util import funs, converters  # pylint: disable=no-name-in-module
from util.emoji_chars import emoji_chars


def c_to_f(c: float) -> float:
    return (c * 9 / 5) + 32


def f_to_c(f: float) -> float:
    return (f - 32) * (5 / 9)


# noinspection SpellCheckingInspection,PyPep8Naming,PyIncorrectDocstring
class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_client = dialogflow.SessionsClient()

    @commands.command(aliases=["send"])
    async def say(self, ctx, *, message):
        """Have the bot say something. Have fun!

        Args:
            message: The message you want to say
        """

        await ctx.channel.trigger_typing()
        sentMessage = await ctx.send(message)
        await funs.log(ctx, message, sentMessage)
        await ctx.message.delete(delay=5)

    @commands.command(aliases=["sendembed", "embed"])
    async def sayembed(self, ctx, *, message):
        """
        Have the bot say something in embeds. Have fun!
        """
        await ctx.channel.trigger_typing()

        embed = discord.Embed()
        splitedMessage = message.split('\n')
        for i in splitedMessage:
            if i.startswith('t'):
                embed.title = i[2:]
            elif i.startswith('d'):
                embed.description = i[2:]
            elif i.startswith('f'):
                embed.set_footer(text=i[2:])
            elif i.startswith('c'):
                embed.colour = discord.Colour(int(f'0x{i[2:].strip()}', 16))

        fields = [j.strip('?').split(',') for j in splitedMessage if j.startswith("?")]
        for f in fields:
            embed.add_field(name=f[0], value=f[1], inline=f[2].strip() != 'false')
        sentMessage = await ctx.send(embed=embed)

        embed.timestamp = ctx.message.created_at
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        embed.add_field(name='Message', value=f'[Jump To Message]({sentMessage.jump_url})', inline=False)

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(logWebhook, adapter=discord.AsyncWebhookAdapter(session))
            await webhook.send(embed=embed, username='sayembed')

    @commands.command(aliases=["addreaction"])
    async def react(self, ctx, msg: discord.Message, text):
        """
        Add the given reactions to a message
        """

        sent = []
        for i in text:
            if re.fullmatch(r'[a-z]', i, re.IGNORECASE):
                await msg.add_reaction(emoji_chars[str(i).lower()])
                sent.append(i)

        await funs.log(ctx, text, ctx.message, ''.join(sent))

    @commands.command()
    async def totogglecase(self, ctx, *, msg):
        """
        Convert string to toggle case
        """
        out = ""
        message = str(msg)
        for i in range(0, len(message)):
            out += message[i].lower() if (i % 2 == 0) else message[i].upper()

        sentMessage = await ctx.send(out)
        await funs.log(ctx, msg, sentMessage, out)
        await ctx.message.delete(delay=5)

    @commands.command(aliases=["yell"])
    async def touppercase(self, ctx, *, msg):
        """
        Convert string to toggle case
        """
        out = str(msg).upper()
        sentMessage = await ctx.send(out)
        await funs.log(ctx, msg, sentMessage, out)
        await ctx.message.delete()

    @commands.command(aliases=["wide"])
    async def addspaces(self, ctx, msg: str, spaces: int = 3):
        """
        Adds 3 spaces in between every character.
        If the first arg is a number, it will use that for the number of spaces instead.
        """

        between = spaces * ' '
        out = between.join(list(str(msg)))
        sentMessage = await ctx.send(out)
        await funs.log(ctx, msg, sentMessage, out)
        await ctx.message.delete(delay=5)

    @commands.command()
    async def flip(self, ctx, *, msg):
        """
        Converts given text to flipped unicode characters
        """
        FLIP_RANGES = [
            (string.ascii_lowercase, "ɐqɔpǝɟƃɥᴉɾʞꞁɯuodbɹsʇnʌʍxʎz"),
            (string.ascii_uppercase, "ⱯᗺƆᗡƎᖵ⅁HIᒋ⋊ꞀWNOԀꝹᴚS⊥ႶɅMX⅄Z"),
            (string.digits, "0ІᘔƐᔭ59Ɫ86"),
            (string.punctuation, "¡„#$%⅋,)(*+'-˙/:؛>=<¿@]\\[ᵥ‾`}|{~"),
        ]

        msgBack = ""
        for c in list(msg):
            for r in range(len(FLIP_RANGES)):
                try:
                    p = FLIP_RANGES[r][0].index(c)
                    if not p == -1:
                        newC = FLIP_RANGES[r][1][p]
                        msgBack += newC
                        break
                except ValueError:
                    msgBack += ' '
                    continue

        out = ' '.join(msgBack.split())
        sentMessage = await ctx.send(out)
        await funs.log(ctx, msg, sentMessage, out)
        await ctx.message.delete(delay=5)

    @commands.command(aliases=["rick", "rickroll"])
    async def rickroulette(self, ctx):
        """
        Rickroll bot. Lose/win
        """
        await ctx.channel.trigger_typing()
        rick = "https://tenor.com/view/never-gonna-give-you-up-dont-give-never-give-up-gif-14414705"
        await asyncio.sleep(3)
        await ctx.send(f"Get rick rolled\n {rick}")

    @commands.command(aliases=["to_c"])
    async def toc(self, ctx, message):
        """
        Convert fahrenheit to celsius.
        Format: '>toc <temp in f>'. 
        Example: '>toc 69'.
        """

        try:
            await ctx.send(f'{int(f_to_c(float(message)))}°C')
        except Exception as identifier:
            await ctx.send(f"Bruh...\nDon't you know how to follow instructions\nError: {identifier}")

    @commands.command(aliases=["to_f"])
    async def tof(self, ctx, message):
        """
        Convert celsius to fahrenheit.
        Format: '>tof <temp in c'.
        Example: '>tof 20.5'.
        """

        try:
            await ctx.send(f'{int(c_to_f(float(message)))}°F')
        except Exception as identifier:
            await ctx.send(f"Bruh...\nDon't you know how to follow instructions\nError: {identifier}")

    @commands.command()
    async def poll(self, ctx, question, *answers):
        """
        Start a poll.
        If answers/questions contain spaces put it in quotes
        Example:
            >poll "Do you like bacon" yes

        Args:
            question: The question you want to ask. This will be title of embed
            answers: The answers for the poll. If omitted, it will default to yes/no. Max of 10 answers are allowed
        """

        if answers == ():
            msg = await ctx.send(f"**📊 {question}**")
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

        elif len(answers) < 10:
            letter_emote = list(emoji_chars.values())
            inner = ""
            for i in range(len(answers)):
                inner += f"{letter_emote[i]} {answers[i]}\n"
            embed = discord.Embed(title=f"**📊 {question}**", description=inner, color=funs.random_discord_color())
            msg = await ctx.send(embed=embed)
            for i in range(len(answers)):
                await msg.add_reaction(letter_emote[i])

    # noinspection PyUnresolvedReferences
    @commands.command(aliases=['talk', 't'])
    async def chat(self, ctx, *, text):
        """Talk to me"""
        session = self.session_client.session_path(project_id, ctx.author.id)

        text_input = dialogflow.types.TextInput(text=text, language_code='en-US')

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = self.session_client.detect_intent(session=session, query_input=query_input)

        await ctx.send(response.query_result.fulfillment_text)

    @commands.command()
    async def about(self, ctx):
        repo = git.Repo()
        commits = list(repo.iter_commits())[:3]
        out = []
        for commit in commits:
            message = commit.message.split('\n')[0]
            time = str(datetime.now(tz=commit.authored_datetime.tzinfo) - commit.authored_datetime).split('.')[0][:-3] \
                       .replace(':', ' hours, ') + ' minutes'
            out.append(f"[`{commit.hexsha[0:7]}`](https://github.com/hamza1311/BitchBot/commit/{commit.hexsha}) "
                       f"{message} - {commit.author}; {time} ago")

        joined = '\n'.join(out)
        embed = discord.Embed(color=funs.random_discord_color(), description=f"Latest commits:\n{joined}")
        owner = self.bot.get_user(self.bot.owner_id)
        embed.set_author(name=f"{owner.name}#{owner.discriminator}", icon_url=owner.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name="Source", value=f"[GitHub Respositiory]({list(repo.remote('origin').urls)[0]})")
        embed.add_field(name="Deployed branch", value=repo.active_branch)
        embed.add_field(name='Comamnds', value=f"{len(self.bot.cogs)} Cogs loaded\n{len(self.bot.commands)} commands")
        members = list(self.bot.get_all_members())
        embed.add_field(name='Members', value=f'Total: {len(members)}\nUnique: {len(set(m.id for m in members))}')
        embed.set_footer(text=f'Written in discord.py v{discord.__version__}',
                         icon_url='https://i.imgur.com/RPrw70n.png')

        await ctx.send(embed=embed)

    @commands.command()
    async def owoize(self, ctx, *, message):
        owoized = text_to_owo(message)
        sent = await ctx.send(owoized)
        await funs.log(ctx, message, sent, owoized)

    # noinspection PyMethodMayBeStatic
    def user_presentable_perms(self, permissmions):
        allowed = []
        denied = []
        for perm in permissmions:
            if perm[1]:
                allowed.append(perm[0])
            else:
                denied.append(perm[0])

        def make_user_presentable(perms):
            return ', '.join(perms).replace('_', ' ')\
                .replace('guild', 'server').title()

        new_line = '\n'
        return f"**Allowed**\n{make_user_presentable(allowed)}\n" \
               f"{'' if len(denied) == 0 else f'**Denied**{new_line}{make_user_presentable(denied)}'}"

    @commands.command(aliases=['whois'])
    async def info(self, ctx, member: Union[discord.Member, converters.FetchedUser] = None):
        user = member or ctx.author

        embed = discord.Embed(color=user.color)
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='ID', value=user.id)
        embed.add_field(name='Created At', value=user.created_at)

        # access of member specific props ahead so send the message and return if `user` is not a `Member`
        if not isinstance(user, discord.Member):
            return await ctx.send(embed=embed)

        embed.add_field(name='Joined At', value=user.joined_at)
        if user.premium_since is not None:
            embed.add_field(name='Last boosted on', value=user.premium_since)
        embed.add_field(name='Is on mobile', value=user.is_on_mobile())
        embed.add_field(name='Permissions', value=self.user_presentable_perms(user.guild_permissions), inline=False)
        sorted_roles = sorted(user.roles[1:], key=lambda x: x.position, reverse=True)
        embed.add_field(name='Roles', value=', '.join([r.mention for r in sorted_roles]), inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
