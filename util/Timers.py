import asyncio

from services import TimersService


class Timers:
    def __init__(self, bot):
        self.bot = bot
        self.timers_service = TimersService(bot.db)
        self.bot.loop.create_task(self.refresh_timer())

    async def create_timer(self, timer):
        # TODO: don't insert if timer expires less than, say, 5 minutes
        await self.timers_service.insert(timer)

    async def refresh_timer(self):
        while not self.bot.is_closed():
            print('hitting db now')
            timers = await self.timers_service.fetch_past_timers()
            for timer in timers:
                print('deleting ', timer)
                self.bot.dispatch(timer.event, timer)
                await self.timers_service.delete(timer)
            await asyncio.sleep(10)
