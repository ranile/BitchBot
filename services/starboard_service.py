from database.sql import SQL
from resources.starboard import Starboard


class StarboardService:
    def __init__(self, pool):
        self.pool = pool

    async def get(self, message_or_star_id, guild_id):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetchrow('''
                select *
                from starboard
                where (message_id = $1 or id = $1) and guild_id = $2;
            ''', int(message_or_star_id), guild_id)

            return Starboard.convert(fetched) if fetched is not None else None

    async def star(self, reaction):
        async with self.pool.acquire() as connection:
            message = reaction.message
            try:
                attachment = message.attachments[0].url
            except IndexError:
                attachment = None

            starred = await connection.fetchrow('''
                insert into Starboard (message_id, channel_id, guild_id, message_content, attachment, stars_count, author_id)
                values ($1, $2, $3, $4, $5, $6, $7)
                on conflict(message_id) do update set stars_count = $6
                returning *, (stars_count >=
                              (select guildconfig.star_limit from guildconfig where guildconfig.guild_id = starboard.guild_id)) as should_send
                ''', message.id, message.channel.id, message.guild.id,
                                                message.content if message.system_content != '' else None,
                                                attachment, reaction.count, message.author.id)

            return starred['should_send'], Starboard.convert(starred)

    async def unstar(self, reaction):
        message = reaction.message
        async with self.pool.acquire() as connection:
            unstarred = await connection.fetchrow('''
                    update starboard
                    set stars_count = starboard.stars_count - 1
                    where message_id = $1 and channel_id = $2 and guild_id = $3
                    returning *;
                ''', message.id, message.channel.id, message.guild.id)

            return Starboard.convert(unstarred)

    async def guild_top_stats(self, guild):
        query = '''
        select author_id, count(author_id) from Starboard
        where guild_id = $1
        group by author_id
        order by count desc
        limit 10;
        '''
        async with self.pool.acquire() as connection:
            fetched = await connection.fetch(query, guild.id)
        result = []
        for stared in fetched:
            member = guild.get_member(stared['author_id'])
            if member is None:
                continue
            res = {
                'author': member,
                'count': stared['count']
            }

            result.append(res)

        return result

    async def my_stats(self, ctx):
        query = '''
        select author_id, count(author_id) from Starboard
        where guild_id = $1 and author_id = $2
        group by author_id
        order by count desc;
        '''
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, ctx.guild.id, ctx.author.id)

    @classmethod
    def sql(cls):
        return SQL(createTable='''
            create table if not exists Starboard
            (
                id              serial primary key,
                message_id      bigint    not null,
                guild_id        bigint    not null,
                channel_id      bigint    not null,
                author_id       bigint    not null,
                started_at      timestamp not null default now(),
                message_content text,
                attachment      text,
                stars_count     int       not null
            );
            
            create unique index if not exists unique_message on Starboard (message_id);
            ''')
