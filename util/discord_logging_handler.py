import logging
from datetime import datetime

import aiohttp
import discord

import keys


class DiscordLoggingHandler(logging.Handler):

    def __init__(self, loop, client_session, level=logging.INFO):
        self.loop = loop
        self.client_session = client_session
        super().__init__(level)

    async def send_log(self, record: logging.LogRecord):
        self.format(record)
        embed = discord.Embed(
            title=record.levelname,
            description=f'```{record.message}```',
            timestamp=datetime.strptime(record.asctime[:-4], '%Y-%m-%d %H:%M:%S')
        )
        embed.add_field(name='Module', value=f'`{record.name}`: `{record.module}`')
        try:
            webhook = discord.Webhook.from_url(
                keys.logWebhook,
                adapter=discord.AsyncWebhookAdapter(self.client_session))
            await webhook.send(embed=embed)
        except (RuntimeError, BaseException):
            webhook = discord.Webhook.from_url(
                keys.logWebhook,
                adapter=discord.RequestsWebhookAdapter())
            webhook.send(embed=embed)

    def emit(self, record: logging.LogRecord):
        self.loop.create_task(self.send_log(record))
