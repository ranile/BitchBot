import asyncio
import random
import re
import unicodedata
import discord
from discord.ext import commands as dpy_commands
from keys import rabbitWebhook
from resources import Counter
import util
from util import commands

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
# old = r"(kaylie'?s? ?(man)|([rw])( +)?([a@])( +)?b(( +)?b)?( +)?i( +)?t(man)?|\br ?word\b|(elizabeth|liz)'?s ?hoe)"
rabbit_match = r'(kaylie\'?s? ?(man)|(r)( +)?(a)( +)?b(( +)?b)( +)?i( +)?t ?(man)?|\br ?word\b)'
THE_CAUSE = 505655510263922700
RABBIT_WEBHOOK = 651333096829878272
HAIKU_BOT = 372175794895585280


async def get_counter(db, name, value):
    counter = await db.fetchrow(
        f"""select count, summoned_at, summoned_by from Counters 
            where name = 'rabbit' and {name} = $1;""", value)
    return Counter.convert(counter)


async def insert_counter(db, res):
    inserted = await db.fetchrow(
        """insert into Counters (name, summoned_at, summoned_by)
        values ($1, $2, $3)
        returning name, count, summoned_at, summoned_by;""",
        res.name, res.summonedAt, res.summonedBy)
    return Counter.convert(inserted)


async def get_count(db, counter_name):
    fetched = await db.fetchrow('''
        select count(count), name
        from counters
        where name = $1
        group by name;
        ''', counter_name)
    return fetched['count']


async def get_top_counts(db, limit, guild_members):
    return await db.fetch('''
        select summoned_by, actual_count as count
        from (
                 select summoned_by, count(count) as actual_count
                 from counters
                 where name = 'rabbit'
                 group by summoned_by
                 order by actual_count desc
             ) as ic
        where ic.summoned_by = any ($2::bigint[])
        limit $1;
    ''', limit, [x.id for x in guild_members])


async def get_members_counted_count(db, member_id):
    fetched = await db.fetchrow(
        '''
            select summoned_by, count(count) from counters
            where name = 'rabbit' and summoned_by = $1
            group by summoned_by
            order by count(count) desc;
        ''', member_id)
    return fetched['count'] if fetched is not None else None


async def get_counted_count(db, count_to_fetch):
    fetched = await db.fetchrow('''
        select *
        from (
                 select name, summoned_by, summoned_at, row_number() over (order by summoned_at) as count
                 from counters
                 where name = 'rabbit'
             ) as ic
        where count = $1;
    ''', count_to_fetch)

    return Counter.convert(fetched)


async def create_counters_table(pool):
    async with pool.acquire() as connection:
        await connection.execute('''
        create table if not exists Counters
        (
            count serial not null primary key,
            name text not null,
            summoned_by bigint not null,
            summoned_at int not null
        );
        ''')


class Cause(dpy_commands.Cog, name="The Cause"):
    def __init__(self, bot):
        self.bot = bot

        # Rabbit stuff
        self.isRabbitOnCooldown = False
        self.rabbitCooldownTime = 10  # TODO: Make it use CooldownMapping
        self.rabbitAlreadySummoned = []

        self.bot.loop.create_task(create_counters_table(bot.db))

    def cog_check(self, ctx):
        return ctx.guild is not None and True  # ctx.guild.id == THE_CAUSE

    async def put_rabbit_on_cooldown(self):
        self.isRabbitOnCooldown = True
        await asyncio.sleep(self.rabbitCooldownTime)
        self.isRabbitOnCooldown = False

    # noinspection PyMethodMayBeStatic
    def get_rabbit_pfp(self):
        return f'https://firebasestorage.googleapis.com/v0/b/bitchbot-discordbot.appspot.com/o/' \
               f'images%2Frabbit%2Frabbitman{random.randint(1, 9)}.jpg?alt=media'

    async def send_counter_update(self, msg, username, pfp):
        webhook = discord.Webhook.from_url(rabbitWebhook, adapter=discord.AsyncWebhookAdapter(self.bot.clientSession))
        await webhook.send(msg, username=username, avatar_url=pfp)

    async def increment_rabbit(self, db, message, summoned_by=None, rabbit=random.choice(rabbits)):
        if summoned_by is None:
            summoned_by = message.author

        await insert_counter(db, Counter(summonedBy=summoned_by.id, name=Counter.RABBIT))
        count = await get_count(db, Counter.RABBIT)
        if not self.isRabbitOnCooldown:
            await self.send_counter_update(
                f"{summoned_by.display_name} called the rabbit {rabbit}, "
                f"Kaylie's man {rabbit}.\nRabbit count: {count}\n"
                f"[Message](<{message.jump_url}>)", 'Rabbit', self.get_rabbit_pfp())
            # await message.add_reaction(rabbit)

        self.rabbitAlreadySummoned.append(message.id)
        await self.put_rabbit_on_cooldown()

    async def increment_haiku(self, db, author, text):
        await insert_counter(db, Counter(summonedBy=author.id, name=Counter.HAIKU))
        count = await get_count(db, Counter.HAIKU)
        split = text.split('\n')
        sent_text = ' '.join(split).replace('*', '')
        await self.send_counter_update(
            f"{author.display_name} summoned HaikuBot with message:\n> {sent_text}\nHaiku counter: {count}",
            'HaikuBot Counter', None)

    @dpy_commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user or message.guild is None or message.guild.id != THE_CAUSE:
            return

        normalized = unicodedata.normalize('NFKD', message.content).encode('ascii', 'ignore').decode('ascii')
        if re.search(rabbit_match, normalized, re.IGNORECASE) and message.webhook_id != RABBIT_WEBHOOK:
            async with self.bot.db.acquire() as db:
                await self.increment_rabbit(db, message)

        elif message.author.id == HAIKU_BOT:

            embed: discord.Embed = message.embeds[0]
            author = message.guild.get_member_named(embed.footer.text[2:])
            text = embed.description
            async with self.bot.db.acquire() as db:
                await self.increment_haiku(db, author, text)

    @dpy_commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if user.id == self.bot.user.id or message.guild is None or message.guild.id != THE_CAUSE:
            return

        if str(reaction) in rabbits:
            if message.id in self.rabbitAlreadySummoned or self.isRabbitOnCooldown:
                return

            async with self.bot.db.acquire() as db:
                await self.increment_rabbit(
                    db, message, summoned_by=user,
                    rabbit=[r for r in rabbits if r != str(reaction)][0])

    @commands.group(invoke_without_command=True, aliases=["kayliesman"])
    async def rabbit(self, ctx):
        await ctx.channel.send(embed=discord.Embed().set_image(url=self.get_rabbit_pfp()))

    @rabbit.group(name='stats', invoke_without_command=True, wants_db=True)
    async def stats(self, ctx, member: discord.Member = None):
        if member is not None:
            of = member.id
        else:
            of = ctx.author.id
        print(ctx.db, ctx.command.wants_db)
        count = await get_members_counted_count(ctx.db, of)

        await ctx.send(f'{"You have" if of == ctx.author.id else f"{member.display_name} has" } '
                       f'called rabbit {count} times')

    @stats.command(wants_db=True)
    async def top(self, ctx, limit=10):
        fetched = await get_top_counts(ctx.db, limit, ctx.guild.members)

        length = 0
        paginator = dpy_commands.Paginator(prefix='```md')
        for item in fetched:
            member = ctx.guild.get_member(item['summoned_by'])
            if member is None:
                continue
            line = f"{member.display_name} ({member.name}#{member.discriminator}): {item['count']}"
            paginator.add_line(line)
            if length < len(line):
                length = len(line)

        count = await get_members_counted_count(ctx.db, ctx.author.id)

        paginator.add_line()
        paginator.add_line('-' * length)
        paginator.add_line(f"You: {count}")

        for page in paginator.pages:
            await ctx.send(page)

    @rabbit.command(name='show', wants_db=True)
    async def rabbit_show(self, ctx, count: int):
        """
        Shows details about given rabbit count

        Example:
            `rabbit show 69`

        Args:
            count: The rabbit count
        """

        rabbit = await get_counted_count(ctx.db, count)
        author = ctx.guild.get_member(rabbit.summonedBy)
        author_name = f'{str(author)} ({author.display_name})'
        if author is None:
            author = self.bot.get_user(rabbit.summonedBy)
            author_name = str(author)

        if author is None:
            author = await self.bot.fetch_user(rabbit.summonedBy)
            author_name = str(author)

        embed = discord.Embed(timestamp=rabbit.summonedAt, color=util.random_discord_color())
        embed.set_author(name=author_name, icon_url=author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def baby(self, ctx):
        """Sends a Baby picture"""
        url = 'https://firebasestorage.googleapis.com/v0/b/bitchbot-discordbot.appspot.com/o/' \
              f'images%2Fbaby%2Fbaby{random.randint(1, 9)}.jpg?alt=media'
        await ctx.channel.send(embed=discord.Embed().set_image(url=url))


def setup(bot):
    bot.add_cog(Cause(bot))
