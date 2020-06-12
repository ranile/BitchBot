from discord.ext import commands as dpy_commands
import typing
import asyncpg
import lavalink

__all__ = ('Context',)

from util.commands import Command


class Context(dpy_commands.Context):
    command: Command

    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.db: typing.Optional[asyncpg.Connection] = None

    @property
    def player(self) -> typing.Optional[lavalink.DefaultPlayer]:
        # Can't type hint properly because of circular imports
        # noinspection PyUnresolvedReferences
        return self.bot.lavalink.player_manager.get(self.guild.id)
