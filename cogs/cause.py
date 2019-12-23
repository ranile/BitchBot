import asyncio
import re
import unicodedata
import random
import discord
from discord.ext import commands

from resources import RabbitCounter
from services import RabbitService
from util import funs

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
rabbit_match = r"(kaylie'?s? ?(man)|r( +)?(a|@)( +)?b( +)?b( +)?i( +)?t(man)?|r ?word)"
THE_CAUSE = 505655510263922700
RABBIT_WEBHOOK = 651333096829878272

RES_PATH = 'res/'


class Cause(commands.Cog, name="The Cause"):
    def __init__(self, bot):
        self.bot = bot

        # Rabbit stuff
        self.isRabbitOnCooldown = False
        self.rabbitCooldownTime = 10
        self.rabbitAlreadySummoned = []

    def cog_check(self, ctx):
        return ctx.guild.id == THE_CAUSE

    async def put_rabbit_on_cooldown(self):
        self.isRabbitOnCooldown = True
        await asyncio.sleep(self.rabbitCooldownTime)
        self.isRabbitOnCooldown = False

    async def increment_rabbit(self, message, rabbit=random.choice(rabbits)):
        inserted_rabbit = await RabbitService.insert(RabbitCounter(summonedBy=message.author.id))

        if not self.isRabbitOnCooldown:
            await funs.sendRabbitCounterUpdate(self.bot,
                                               f"{message.author.display_name} called the rabbit {rabbit}, "
                                               f"Kaylie's man {rabbit}.\nRabbit count: {inserted_rabbit.count}")
            await message.add_reaction(rabbit)

        self.rabbitAlreadySummoned.append(message.id)
        await self.put_rabbit_on_cooldown()

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        normalized = unicodedata.normalize('NFKD', message.content).encode('ascii', 'ignore').decode('ascii')

        if (re.search(rabbit_match, normalized, re.IGNORECASE) and
                message.guild.id == THE_CAUSE and
                message.webhook_id != RABBIT_WEBHOOK):
            await self.increment_rabbit(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user.id == self.bot.user.id:
            return

        if str(reaction) in rabbits:
            if reaction.message.id in self.rabbitAlreadySummoned or self.isRabbitOnCooldown:
                return

            await self.increment_rabbit(reaction.message, rabbit=[r for r in rabbits if r != str(reaction)][0])

    @commands.group(invoke_without_command=True, aliases=["kayliesman"])
    async def rabbit(self, ctx):

        await ctx.channel.send(file=discord.File(f'{RES_PATH}rabbitman{random.randint(1, 9)}.jpg'))

    @rabbit.group(invoke_without_command=True)
    async def stats(self, ctx, member: discord.Member = None):
        if member is not None:
            of = member.id
        else:
            of = ctx.author.id

        query = """select count(count) from counters where summoned_by = $1 and name = 'rabbit';"""
        count = await self.bot.db.fetchval(query, of)

        await ctx.send(f'{"You" if of == ctx.author.id else member.display_name} have called rabbit {count} times')

    @stats.command()
    async def top(self, ctx, limit=10):
        fetched = await self.bot.db.fetch('''
        select summoned_by, count(count) from counters
        where name = 'rabbit'
        group by summoned_by
        order by count(count) desc
        limit $1;
        ''', limit)
        length = 0
        paginator = commands.Paginator(prefix='```md')
        for item in fetched:
            member = ctx.guild.get_member(item['summoned_by'])
            line = f"{member.display_name} ({member.name}#{member.discriminator}): {item['count']}"
            paginator.add_line(line)
            if length < len(line):
                length = len(line)

        fetched_me = await self.bot.db.fetchrow('''
        select summoned_by, count(count) from counters
        where name = 'rabbit' and summoned_by = $1
        group by summoned_by
        order by count(count) desc;
        ''', ctx.author.id)

        paginator.add_line()
        paginator.add_line('-' * length)
        paginator.add_line(f"You: {fetched_me['count']}")

        for page in paginator.pages:
            await ctx.send(page)

    @commands.command()
    async def baby(self, ctx):
        """Sends a Baby picture"""

        await ctx.channel.send(file=discord.File(f'{RES_PATH}baby{random.randint(1, 9)}.jpg'))


def setup(bot):
    bot.add_cog(Cause(bot))
