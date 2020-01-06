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

    @classmethod
    async def get_all(cls, guild_id, user_id=None):
        query = '''
        select * from Warnings
        where guild_id = $1
        '''
        if user_id is not None:
            query += '''
            and warned_user_id = $2
            order by warned_user_id;
            '''
            fetched = await database.connection.fetch(query, guild_id, user_id)
            return Warn.convertMany(fetched)
        else:
            query += '\norder by warned_user_id;'
            fetched = await database.connection.fetch(query, guild_id)
            return Warn.convertMany(fetched)
