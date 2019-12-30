from database import database
import asyncpg

from database.sql import SQL
from resources.starboard import Starboard


class StarboardService:

    @classmethod
    async def get(cls, message_or_star_id, guild_id):
        fetched = await database.connection.fetchrow('''
            select *
            from starboard
            where (message_id = $1 or id = $1) and guild_id = $2;
        ''', int(message_or_star_id), guild_id)

        return Starboard.convert(fetched) if fetched is not None else None

    @classmethod
    async def star(cls, reaction):
        message = reaction.message
        should_send = False
        try:
            should_send = True

            try:
                attachment = message.attachments[0].url
            except IndexError:
                attachment = None

            starred = await database.connection.fetchrow('''
                insert into Starboard (message_id, channel_id, guild_id, message_content, attachment, stars_count, author_id)
                values ($1, $2, $3, $4, $5, $6, $7)
                returning *;
            ''', message.id, message.channel.id, message.guild.id, message.content if message.content != '' else None,
                                                         attachment, reaction.count, message.author.id)
        except asyncpg.exceptions.UniqueViolationError:
            starred = await database.connection.fetchrow('''
                update starboard
                set stars_count = $4
                where message_id = $1 and channel_id = $2 and guild_id = $3
                returning *;
            ''', message.id, message.channel.id, message.guild.id, reaction.count)

        return should_send, Starboard.convert(starred)

    @classmethod
    async def unstar(cls, reaction):
        message = reaction.message
        unstarred = await database.connection.fetchrow('''
                update starboard
                set stars_count = starboard.stars_count - 1
                where message_id = $1 and channel_id = $2 and guild_id = $3
                returning *;
            ''', message.id, message.channel.id, message.guild.id)

        return Starboard.convert(unstarred)

    @classmethod
    async def guild_top_stats(cls, guild):
        query = '''
        select author_id, count(author_id) from Starboard
        where guild_id = $1
        group by author_id
        order by count desc
        limit 10;
        '''

        fetched = await database.connection.fetch(query, guild.id)
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

    @classmethod
    async def my_stats(cls, ctx):
        query = '''
        select author_id, count(author_id) from Starboard
        where guild_id = $1 and author_id = $2
        group by author_id
        order by count desc;
        '''

        return await database.connection.fetchrow(query, ctx.guild.id, ctx.author.id)
