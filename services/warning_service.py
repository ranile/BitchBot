import asyncpg

from resources import Warn


class WarningsService:

    @staticmethod
    async def insert(db: asyncpg.Connection, warn: Warn) -> Warn:
        inserted = await db.fetchrow('''
            insert into Warnings (reason, warned_by_id, warned_user_id, guild_id)
            values ($1, $2, $3, $4)
            returning *;
        ''', warn.reason, warn.warned_by_id, warn.warned_user_id, warn.guild_id)

        return Warn.convert(inserted)

    @staticmethod
    async def get_all(db: asyncpg.Connection, guild_id: int, user_id: int = None) -> list[Warn]:

        if not isinstance(user_id, int):
            raise TypeError(f'user_id must be an int')

        query = f'''
            select * from Warnings
            where guild_id = $1 {'' if user_id is None else f'and warned_user_id = {user_id}'}
            order by warned_user_id;
        '''
        fetched = await db.fetch(query, guild_id)

        return Warn.convertMany(fetched)

    initial_sql = '''
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
