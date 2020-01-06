from database import database
from database.sql import SQL
from resources import Mute


class MuteService:
    @classmethod
    async def insert(cls, mute):
        query = await database.connection.fetchrow('''
            insert into Mutes (reason, muted_by_id, muted_user_id, guild_id)
            values ($1, $2, $3, $4)
            returning *;
        ''', mute.reason, mute.muted_by_id, mute.muted_user_id, mute.guild_id)

        return Mute.convert(query)

    @classmethod
    async def delete(cls, guild_id, muted_user_id):
        return await database.connection.execute('''
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
