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
    async def insert(cls, guild):
        pass

    @classmethod
    def sql(cls):
        return SQL(createTable='''
        create table if not exists GuildConfig
        (
            guild_id          bigint primary key,
            starboard_channel bigint
        )
        ''')
