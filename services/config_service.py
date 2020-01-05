import asyncpg

from database import database
from database.sql import SQL
from resources.guild_config import GuildConfig


class GuildConfigService:

    @classmethod
    async def get(cls, guild_id):
        fetched = await database.connection.fetchrow('''
        select * from GuildConfig
        where guild_id = $1
        ''', guild_id)
        return GuildConfig.convert(fetched)

    @classmethod
    async def insert(cls, config):
        try:
            inserted = await database.connection.fetchrow('''
            insert into GuildConfig (guild_id, starboard_channel)
            values ($1, $2)
            returning *;
            ''', config.guild_id, config.starboard_channel)

        except asyncpg.exceptions.UniqueViolationError:
            inserted = await database.connection.fetchrow('''
            update GuildConfig 
            set starboard_channel = $1
            where guild_id = $2
            returning *;
            ''', config.starboard_channel, config.guild_id)

        return GuildConfig.convert(inserted)

    @classmethod
    def sql(cls):
        return SQL(createTable='''
        create table if not exists GuildConfig
        (
            guild_id          bigint primary key,
            starboard_channel bigint,
            event_log_webhook text
        )
        ''')
