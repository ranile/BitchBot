import json

from resources import Timer


class TimersService:
    def __init__(self, pool):
        self.pool = pool

    async def insert(self, timer):
        async with self.pool.acquire() as conn:
            await conn.execute('''
            insert into Timers (event, created_at, expires_at, extras)
            values ($1, $2, $3, $4::jsonb);
            ''', timer.event, timer.created_at, timer.expires_at, json.dumps(timer.kwargs))

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
