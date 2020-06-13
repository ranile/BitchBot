import typing
from datetime import datetime

import discord
from discord.enums import Enum

_loggers = {}


class Levels(Enum):
    value: str

    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3
    EXCEPTION = 4
    CRITICAL = 5


_default = True


class Logger:
    _webhook: discord.Webhook
    _colors: typing.Dict[Levels, typing.Union[discord.Color, int]]
    module: str
    _force_embeds: bool

    @classmethod
    def obtain(cls, module):
        try:
            return _loggers[module]
        except KeyError:
            logger = cls()
            logger.module = module
            _loggers[module] = logger
            return logger

    @classmethod
    def init(
            cls,
            webhook: discord.Webhook,
            colors: typing.Dict[Levels, typing.Union[discord.Color, int]],
            base_level: Levels,
            *, force_embeds: bool = _default
    ):
        cls._webhook = webhook
        cls._colors = colors
        cls._force_embeds = force_embeds
        cls.base_level = base_level

    def _build_data(
            self,
            level: Levels,
            data: typing.Union[str, discord.Embed],
            make_embed: bool,
            lang='',
    ) -> typing.Dict[str, typing.Union[str, discord.Embed]]:

        if self._force_embeds is False or make_embed is False:
            make_embed = False

        elif self._force_embeds is _default or make_embed is True:
            make_embed = True

        params = {}
        if isinstance(data, str) and make_embed:
            embed = discord.Embed(
                title=level.name.title(),
                description=f'```{lang}\n{data}```\n**Module**: `{self.module}`',
                color=self._colors[level],
                timestamp=datetime.utcnow()
            )
            params['embed'] = embed
        elif isinstance(data, str):
            params['content'] = data
        elif isinstance(data, discord.Embed):
            params['embed'] = data

        return params

    async def _send(self, message_or_embed: typing.Union[str, discord.Embed], level: Levels, force_embeds: bool = True):
        if self.base_level <= level:
            return
        await self._webhook.send(**self._build_data(level, message_or_embed, force_embeds))

    async def debug(self, message_or_embed: typing.Union[str, discord.Embed], *, force_embeds: bool = True):
        await self._send(message_or_embed, Levels.DEBUG, force_embeds)

    async def info(self, message_or_embed: typing.Union[str, discord.Embed], *, force_embeds: bool = True):
        await self._send(message_or_embed, Levels.INFO, force_embeds)

    async def warn(self, message_or_embed: typing.Union[str, discord.Embed], *, force_embeds: bool = True):
        await self._send(message_or_embed, Levels.WARN, force_embeds)

    async def error(self, message_or_embed: typing.Union[str, discord.Embed], *, force_embeds: bool = True):
        await self._send(message_or_embed, Levels.ERROR, force_embeds)

    async def exception(self, exception: Exception):
        pass  # TODO

    async def critical(self, message_or_embed: typing.Union[str, discord.Embed], *, force_embeds: bool = True):
        await self._send(message_or_embed, Levels.CRITICAL, force_embeds)
