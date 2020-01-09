from database.sql import SQL
from resources import Mute


class MuteService:
    def __init__(self, pool):
        self.pool = pool

    async def insert(self, mute):
        async with self.pool.acquire() as connection:
            query = await connection.fetchrow('''
            insert into Mutes (reason, muted_by_id, muted_user_id, guild_id)
            values ($1, $2, $3, $4)
            returning *;
        ''', mute.reason, mute.muted_by_id, mute.muted_user_id, mute.guild_id)

        return Mute.convert(query)

    async def delete(self, guild_id, muted_user_id):
        async with self.pool.acquire() as connection:
            return await connection.execute('''
                delete from Mutes
                where guild_id = $1 and muted_user_id = $2;
            ''', guild_id, muted_user_id)

    @classmethod
    def sql(cls):
        return SQL(
            createTable='''
            create table if not exists Mutes
            (
                id            serial primary key,
                reason        text,
                muted_at      timestamp not null default now(),
                muted_by_id   bigint    not null,
                muted_user_id bigint    not null,
                guild_id      bigint    not null,
                unmute_time   timestamp
            )
            '''
        )
