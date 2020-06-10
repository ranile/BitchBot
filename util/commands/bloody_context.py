from discord.ext import commands as dpy_commands
import typing
import asyncpg

__all__ = ('Context',)

from util.commands import Command


class Context(dpy_commands.Context):
    command: Command

    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.db: typing.Optional[asyncpg.Connection] = None
