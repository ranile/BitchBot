import asyncpg
import typing
from resources import Timer


class TimersService:
    @staticmethod
    async def insert(db: asyncpg.Connection, timer: Timer) -> Timer:
        inserted = await db.fetchrow('''
            insert into Timers (event, created_at, expires_at, extras)
            values ($1, $2, $3, $4::jsonb)
            returning *;
        ''', timer.event, timer.created_at, timer.expires_at, timer.kwargs)

        return Timer.convert(inserted)

    @staticmethod
    async def delete(db: asyncpg.Connection, timer: Timer) -> Timer:
        deleted = await db.fetchrow('''
            delete from timers
            where id = $1
            returning *
        ''', timer.id)
        return Timer.convert(deleted)

    @staticmethod
    async def fetch_past_timers(db: asyncpg.Connection) -> typing.List[Timer]:
        fetched = await db.fetch('''
            select *
            from Timers
            where now() > expires_at;
        ''')
        return Timer.convertMany(fetched)

    @staticmethod
    async def fetch_all_timers(db: asyncpg.Connection) -> typing.List[Timer]:
        fetched = await db.fetch('''
            select *
            from Timers;
        ''')
        return Timer.convertMany(fetched)

    @staticmethod
    async def get_where(db: asyncpg.Connection, *, extras: typing.Dict, limit: int) -> typing.List[Timer]:
        query = '''
            select *
            from Timers where extras @> $1::jsonb
            limit $2;
        '''
        fetched = await db.fetch(query, extras, limit)
        return Timer.convertMany(fetched)

    initial_sql = '''
        create table if not exists Timers
        (
            id         serial primary key,
            event      text      not null,
            created_at timestamp not null,
            expires_at timestamp not null,
            extras     jsonb default '{}'::jsonb
        );
    '''
