import logging
from datetime import datetime

from services import TimersService

from discord.ext import tasks

log = logging.getLogger('BitchBot' + __name__)


class Timers:
    def __init__(self, bot):
        self.bot = bot
        self.current_timers = None
        self.refresh_timer.start()

    async def create_timer(self, timer):
        async with self.bot.db.acquire() as db:
            inserted = await TimersService.insert(db, timer)
        self.current_timers.append(inserted)

    async def delete_timer(self, timer):
        log.debug(f'Deleting timer {timer.id}')
        async with self.bot.db.acquire() as db:
            await TimersService.delete(db, timer)
        self.current_timers.remove(timer)

    def stop(self):
        self.current_timers = None
        self.refresh_timer.cancel()

    def restart(self):
        self.stop()
        self.refresh_timer.start()

    @tasks.loop(seconds=30)
    async def refresh_timer(self):
        if self.current_timers is None:
            log.info('Fetching timers from db')
            async with self.bot.db.acquire() as db:
                self.current_timers = await TimersService.fetch_all_timers(db)

        timers = [x for x in self.current_timers if datetime.utcnow() > x.expires_at]

        for timer in timers:
            self.bot.dispatch(f'{timer.event}_timer_complete', timer)
            await self.delete_timer(timer)

    @refresh_timer.before_loop
    async def before_refresh_timer(self):
        await self.bot.wait_until_ready()

    @refresh_timer.after_loop
    async def after_refresh_timer(self):
        if self.refresh_timer.failed():
            self.stop()
            self.refresh_timer.start()


def setup(bot):
    bot.timers = Timers(bot)


def teardown(bot):
    bot.timers.stop()
