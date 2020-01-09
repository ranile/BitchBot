import asyncpg
from database.sql import SQL
from resources.guild_config import GuildConfig


class GuildConfigService:
    def __init__(self, pool):
        self.pool = pool

    async def get(self, guild_id):
        async with self.pool.acquire() as con:
            fetched = await con.fetchrow('''
            select * from GuildConfig
            where guild_id = $1
            ''', guild_id)
        return GuildConfig.convert(fetched)

    async def insert(self, config):
        async with self.pool.acquire() as connection:
            try:
                inserted = await connection.fetchrow('''
                insert into GuildConfig (guild_id, starboard_channel)
                values ($1, $2)
                returning *;
                ''', config.guild_id, config.starboard_channel)

            except asyncpg.exceptions.UniqueViolationError:
                inserted = await connection.fetchrow('''
                update GuildConfig 
                set starboard_channel = $1
                where guild_id = $2
                returning *;
                ''', config.starboard_channel, config.guild_id)

            return GuildConfig.convert(inserted)

    async def add_mod_role(self, role_id, guild_id):
        query = '''
        update guildconfig
        set mod_roles = guildconfig.mod_roles || $2
        where guild_id = $1
        returning *;
        '''
        async with self.pool.acquire() as connection:
            return GuildConfig.convert(await connection.fetchrow(query, guild_id, [role_id]))

    async def update(self, guild_id, name, value):
        async with self.pool.acquire() as connection:
            fetched = await connection.fetchrow(f'''
                update GuildConfig 
                set {name} = $1
                where guild_id = $2
                returning *;
            ''', value, guild_id)

            return GuildConfig.convert(fetched)

    @classmethod
    def sql(cls):
        return SQL(createTable='''
        create table if not exists GuildConfig
        (
            guild_id          bigint primary key,
            starboard_channel bigint,
            event_log_webhook text,
            mute_role_id bigint,
            mod_roles bigint[] not null default '{}'
        )
        ''')
