import asyncio
from datetime import datetime


class Timers:
    def __init__(self, bot):
        self.bot = bot
        self.pool = bot.db
        self.bot.loop.create_task(self.refresh_timer())

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

    async def refresh_timer(self):
        while not self.bot.is_closed():
            print('hitting db now')
            timers = await self.fetch_from_db()
            for timer in timers:
                print('deleting ', timer)
                self.bot.dispatch(timer['event'], timer)
                await self.delete_timer(timer)
            await asyncio.sleep(10)
