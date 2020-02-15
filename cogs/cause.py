import asyncio
import random
import re
import unicodedata
import discord
from discord.ext import commands
from keys import rabbitWebhook
from resources import Counter
from services import CounterService

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
rabbit_match = r"(kaylie'?s? ?(man)|r( +)?(a|@)( +)?b( +)?b( +)?i( +)?t(man)?|r ?word)"
THE_CAUSE = 505655510263922700
RABBIT_WEBHOOK = 651333096829878272
HAIKU_BOT = 372175794895585280


class Cause(commands.Cog, name="The Cause"):
    def __init__(self, bot):
        self.bot = bot

        # Rabbit stuff
        self.isRabbitOnCooldown = False
        self.rabbitCooldownTime = 10
        self.rabbitAlreadySummoned = []

        self.counter_service = CounterService(bot.db)

    def cog_check(self, ctx):
        return ctx.guild is not None and ctx.guild.id == THE_CAUSE

    async def put_rabbit_on_cooldown(self):
        self.isRabbitOnCooldown = True
        await asyncio.sleep(self.rabbitCooldownTime)
        self.isRabbitOnCooldown = False

    @property
    def _rabbit_pfp(self):
        return f'https://firebasestorage.googleapis.com/v0/b/bitchbot-discordbot.appspot.com/o/' \
               f'images%2Frabbit%2Frabbitman{random.randint(1, 9)}.jpg?alt=media'

    async def send_counter_update(self, msg, username, pfp):
        webhook = discord.Webhook.from_url(rabbitWebhook, adapter=discord.AsyncWebhookAdapter(self.bot.clientSession))
        await webhook.send(msg, username=username, avatar_url=pfp)

    async def increment_rabbit(self, message, rabbit=random.choice(rabbits)):
        await self.counter_service.insert(Counter(summonedBy=message.author.id, name=Counter.RABBIT))
        count = await self.counter_service.count(Counter.RABBIT)
        if not self.isRabbitOnCooldown:
            await self.send_counter_update(
                f"{message.author.display_name} called the rabbit {rabbit}, "
                f"Kaylie's man {rabbit}.\nRabbit count: {count}", 'Rabbit', self._rabbit_pfp)
            await message.add_reaction(rabbit)

        self.rabbitAlreadySummoned.append(message.id)
        await self.put_rabbit_on_cooldown()

    async def increment_haiku(self, author, text):
        await self.counter_service.insert(Counter(summonedBy=author.id, name=Counter.HAIKU))
        count = await self.counter_service.count(Counter.HAIKU)
        split = text.split('\n')
        sent_text = ' '.join(split).replace('*', '')
        await self.send_counter_update(
            f"{author.display_name} summoned HaikuBot with message:\n> {sent_text}\nHaiku counter: {count}",
            'HaikuBot Counter', None)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user or message.guild.id != THE_CAUSE:
            return
        print('yes')
        normalized = unicodedata.normalize('NFKD', message.content).encode('ascii', 'ignore').decode('ascii')
        if (re.search(rabbit_match, normalized, re.IGNORECASE) and
                message.webhook_id != RABBIT_WEBHOOK):
            await self.increment_rabbit(message)
        elif message.author.id == HAIKU_BOT:
            print('yes 2')
            embed: discord.Embed = message.embeds[0]
            author = message.guild.get_member_named(embed.footer.text[2:])
            text = embed.description
            await self.increment_haiku(author, text)

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
        await ctx.channel.send(embed=discord.Embed().set_image(url=self._rabbit_pfp))

    @rabbit.group(invoke_without_command=True)
    async def stats(self, ctx, member: discord.Member = None):
        if member is not None:
            of = member.id
        else:
            of = ctx.author.id

        query = """select count(count) from counters where summoned_by = $1 and name = 'rabbit';"""
        async with self.bot.db.acquire() as conn:
            count = await conn.fetchval(query, of)

        await ctx.send(f'{"You" if of == ctx.author.id else member.display_name} have called rabbit {count} times')

    @stats.command()
    async def top(self, ctx, limit=10):
        async with self.bot.db.acquire() as conn:
            fetched = await conn.fetch('''
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
            if member is None:
                continue
            line = f"{member.display_name} ({member.name}#{member.discriminator}): {item['count']}"
            paginator.add_line(line)
            if length < len(line):
                length = len(line)

        async with self.bot.db.acquire() as conn:
            fetched_me = await conn.fetchrow('''
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
        url = 'https://firebasestorage.googleapis.com/v0/b/bitchbot-discordbot.appspot.com/o/' \
              f'images%2Fbaby%2Fbaby{random.randint(1, 9)}.jpg?alt=media'
        await ctx.channel.send(embed=discord.Embed().set_image(url=url))


def setup(bot):
    bot.add_cog(Cause(bot))
