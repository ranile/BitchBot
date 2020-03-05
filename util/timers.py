import asyncio
import logging
from datetime import datetime

from services import TimersService

log = logging.getLogger('BitchBot' + __name__)


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
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.current_timers is None:
                log.info('Fetching timers from db')
                self.current_timers = await self.timers_service.fetch_past_timers()

            timers = [x for x in self.current_timers if datetime.utcnow() > x.expires_at]

            for timer in timers:
                log.debug(f'Deleting timer {timer.id}')
                self.bot.dispatch(f'{timer.event}_timer_complete', timer)
                await self.timers_service.delete(timer)
                self.current_timers.remove(timer)
            await asyncio.sleep(30)
