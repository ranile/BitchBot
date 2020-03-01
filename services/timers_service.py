import json

from database.sql import SQL
from resources import Timer


class TimersService:
    def __init__(self, pool):
        self.pool = pool

    async def insert(self, timer):
        async with self.pool.acquire() as conn:
            inserted = await conn.fetchrow('''
            insert into Timers (event, created_at, expires_at, extras)
            values ($1, $2, $3, $4::jsonb)
            returning *;
            ''', timer.event, timer.created_at, timer.expires_at, timer.kwargs)

            return Timer.convert(inserted)

    async def delete(self, timer):
        async with self.pool.acquire() as conn:
            deleted = await conn.fetchrow('''
            delete from timers
            where id = $1
            returning *
            ''', timer.id)
        return Timer.convert(deleted)

    async def fetch_past_timers(self):
        async with self.pool.acquire() as conn:
            fetched = await conn.fetch('''
            select *
            from Timers
            where now() > expires_at;
            ''')
        return Timer.convertMany(fetched)

    async def get_where(self, *, extras, limit):
        query = '''
        select *
        from Timers where extras @> $1::jsonb
        limit $2;
        '''
        async with self.pool.acquire() as conn:
            fetched = await conn.fetch(query, extras, limit)
            converted = Timer.convertMany(fetched)
        return converted

    @classmethod
    def sql(cls):
        return SQL(
            createTable='''
            create table if not exists Timers
            (
                id         serial primary key,
                event      text      not null,
                created_at timestamp not null,
                expires_at timestamp not null,
                extras     jsonb default '{}'::jsonb
            );
            '''
        )
