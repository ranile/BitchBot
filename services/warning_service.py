from database import database
from database.sql import SQL
from resources import Warn


class WarningsService:
    @classmethod
    async def insert(cls, warn):
        inserted = await database.connection.fetchrow('''
            insert into Warnings (reason, warned_by_id, warned_user_id, guild_id)
            values ($1, $2, $3, $4)
            returning *;
        ''', warn.reason, warn.warned_by_id, warn.warned_user_id, warn.guild_id)
        return Warn.convert(inserted)

    @classmethod
    def sql(cls):
        return SQL(
            createTable='''
                create table if not exists Warnings
                (
                    id             serial primary key,
                    reason         text      not null,
                    warned_at      timestamp not null default now(),
                    warned_by_id   bigint    not null,
                    warned_user_id bigint    not null,
                    guild_id       bigint    not null
                )
            '''
        )
