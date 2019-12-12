import re
import unicodedata
import random

from discord.ext import commands

from resources import RabbitCounter
from services.rabbit_service import RabbitService
from util import funs

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
rabbit_match = r"(kaylie'?s? ?(man)|r( +)?(a|@)( +)?b( +)?b( +)?i( +)?t(man)?|r ?word)"


class Counters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        normalized = unicodedata.normalize('NFKD', message.content).encode('ascii', 'ignore').decode('ascii')

        if re.search(rabbit_match, normalized, re.IGNORECASE):

            inserted_rabbit = await RabbitService.insert(RabbitCounter(
                summonedBy=message.author.id
            ))
            inserted_rabbit = RabbitCounter.convert(inserted_rabbit)
            print(inserted_rabbit)

            rabbit = random.choice(rabbits)
            await message.channel.send(
                f"{message.author.display_name} called the rabbit {rabbit}, "
                f"Kaylie's man.\n{rabbit} count: {inserted_rabbit.count}")


def setup(bot):
    bot.add_cog(Counters(bot))
