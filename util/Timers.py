from discord.ext import tasks
from datetime import datetime


class Timers:
    def __init__(self, pool):
        self.pool = pool
        self.refresh_timer.start()

    async def fetch_from_db(self):
        async with self.pool.acquire() as conn:
            fetched = await conn.fetch('''
            select *
            from Timers
            where $1 > expires_at;
            ''', datetime.now())
            print(fetched)
        return fetched

    async def delete_timer(self, timer):
        async with self.pool.acquire() as conn:
            val = await conn.fetchval('''
            delete from timers
            where id = $1
            returning id
            ''', timer['id'])
            print(val)

    @tasks.loop(seconds=10)
    async def refresh_timer(self):
        print('hitting db now')
        timers = await self.fetch_from_db()
        for timer in timers:
            print('deleting ', timer)
            # TODO dispatch events
            await self.delete_timer(timer)
