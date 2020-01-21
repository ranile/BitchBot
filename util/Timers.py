import asyncio
from datetime import datetime

from services import TimersService


class Timers:
    def __init__(self, bot):
        self.bot = bot
        self.timers_service = TimersService(bot.db)
        self.current_timers = None
        self.bot.loop.create_task(self.refresh_timer())

    async def create_timer(self, timer):
        # TODO: don't insert if timer expires less than, say, 5 minutes
        inserted = await self.timers_service.insert(timer)
        self.current_timers.append(inserted)

    async def refresh_timer(self):
        while not self.bot.is_closed():
            if self.current_timers is None:
                print('hitting db now')
                self.current_timers = await self.timers_service.fetch_past_timers()

            timers = [x for x in self.current_timers if datetime.utcnow() > x.expires_at]
            print(timers)
            for timer in timers:
                print('deleting ', timer.id)
                self.bot.dispatch(f'{timer.event}_timer_complete', timer)
                await self.timers_service.delete(timer)
                self.current_timers.remove(timer)
            await asyncio.sleep(10)
