import asyncio
import re
import unicodedata
import random
import discord
from discord.ext import commands

from resources import RabbitCounter
from services import RabbitService
from util import funs

THE_RABBIT = '<:rabbitman:593375171880943636>'
THE_RABBIT_V2 = '<:rabbitV2:644894424865832970>'
rabbits = [THE_RABBIT, THE_RABBIT_V2]
rabbit_match = r"(kaylie'?s? ?(man)|r( +)?(a|@)( +)?b( +)?b( +)?i( +)?t(man)?|r ?word)"
THE_CAUSE = 505655510263922700
RABBIT_WEBHOOK = 651333096829878272


class Counters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Rabbit stuff
        self.rabbitRatio = 85
        self.isRabbitOnCooldown = False
        self.rabbitCooldownTime = 10
        self.rabbitAlreadySummoned = []

    async def put_rabbit_on_cooldown(self):
        self.isRabbitOnCooldown = True
        await asyncio.sleep(self.rabbitCooldownTime)
        self.isRabbitOnCooldown = False

    async def increment_rabbit(self, message, rabbit=random.choice(rabbits)):
        inserted_rabbit = await RabbitService.insert(RabbitCounter(summonedBy=message.author.id))

        await funs.sendRabbitCounterUpdate(
            f"{message.author.display_name} called the rabbit {rabbit}, "
            f"Kaylie's man {rabbit}.\nRabbit count: {inserted_rabbit.count}")
        await message.add_reaction(rabbit)

        self.rabbitAlreadySummoned.append(message.id)
        await self.put_rabbit_on_cooldown()

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:
            return

        normalized = unicodedata.normalize('NFKD', message.content).encode('ascii', 'ignore').decode('ascii')

        if (re.search(rabbit_match, normalized, re.IGNORECASE) and
            not self.isRabbitOnCooldown and
            message.guild.id == THE_CAUSE and
            message.webhook_id != RABBIT_WEBHOOK
        ):
            await self.increment_rabbit(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if user.id == self.bot.user.id:
            return

        if str(reaction) in rabbits:
            if reaction.message.id in self.rabbitAlreadySummoned or self.isRabbitOnCooldown:
                return

            await self.increment_rabbit(reaction.message, rabbit=[r for r in rabbits if r != str(reaction)][0])

    @commands.is_owner()
    @commands.command()
    async def setCountersChannel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel to send the counter updates into for the guild

        Args:
            channel: The channel to send counter increment messages in
        """

        await ctx.send('Saved')


def setup(bot):
    bot.add_cog(Counters(bot))
