from database import database
import asyncpg

from database.sql import SQL
from resources.starboard import Starboard


class StarboardService:

    @classmethod
    async def get(cls, star_id):
        pass

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
                insert into Starboard (message_id, channel_id, guild_id, message_content, attachment, stars_count)
                values ($1, $2, $3, $4, $5, $6)
                returning *;
            ''', message.id, message.channel.id, message.guild.id, message.content if message.content != '' else None,
                                                         attachment, reaction.count)
        except asyncpg.exceptions.UniqueViolationError:
            starred = await database.connection.fetchrow('''
                update starboard
                set stars_count = 4
                where message_id = $1 and channel_id = $2 and guild_id = $3
                returning *;
            ''', message.id, message.channel.id, message.guild.id)

        return should_send, Starboard.convert(starred)

    @classmethod
    def sql(cls):
        return SQL(createTable='''
            create table if not exists Starboard
            (
                id              serial primary key,
                message_id      bigint    not null,
                guild_id        bigint    not null,
                channel_id      bigint    not null,
                started_at      timestamp not null default now(),
                message_content text,
                attachment      text,
                stars_count     int       not null
            );
            
            create unique index if not exists unique_message on Starboard (message_id);
            ''')
