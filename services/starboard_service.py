import asyncpg
import discord

from resources.starboard import Starboard


class StarboardService:
    @staticmethod
    async def get(db: asyncpg.Connection, message_or_star_id: int, guild_id: int):
        fetched = await db.fetchrow('''
            select *
            from starboard
            where (message_id = $1 or id = $1) and guild_id = $2;
        ''', int(message_or_star_id), guild_id)

        return Starboard.convert(fetched) if fetched is not None else None

    @staticmethod
    async def star(db: asyncpg.Connection, reaction: discord.Reaction):
        message = reaction.message
        try:
            attachment = message.attachments[0].url
        except IndexError:
            attachment = None

        starred = await db.fetchrow('''
            insert into Starboard (message_id, channel_id, guild_id, message_content, attachment, stars_count, author_id)
            values ($1, $2, $3, $4, $5, $6, $7)
            on conflict(message_id) do update set stars_count = $6
            returning *, (stars_count >=
                          (select guildconfig.star_limit from guildconfig where guildconfig.guild_id = starboard.guild_id)) as should_send
            ''', message.id, message.channel.id, message.guild.id,
                                    message.content if message.system_content != '' else None,
                                    attachment, reaction.count, message.author.id)

        return starred['should_send'], Starboard.convert(starred)

    @staticmethod
    async def unstar(db: asyncpg.Connection, reaction: discord.Reaction):
        message = reaction.message
        unstarred = await db.fetchrow('''
                update starboard
                set stars_count = starboard.stars_count - 1
                where message_id = $1 and channel_id = $2 and guild_id = $3
                returning *;
            ''', message.id, message.channel.id, message.guild.id)

        return Starboard.convert(unstarred)

    @staticmethod
    async def guild_top_stats(db: asyncpg.Connection, guild: discord.Guild):
        query = '''
        select author_id, count(author_id) as count from Starboard
        where guild_id = $1
        group by author_id
        order by count desc
        limit 10;
        '''

        fetched = await db.fetch(query, guild.id)
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

    @staticmethod
    async def members_stats(db: asyncpg.Connection, guild_id: int, member_id: int):
        query = '''
        select author_id, count(author_id) as count from Starboard
        where guild_id = $1 and author_id = $2
        group by author_id
        order by count desc;
        '''

        return await db.fetchrow(query, guild_id, member_id)

    initial_sql = '''
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
    '''
