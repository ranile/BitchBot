from discord.ext import commands as dpy_commands

__all__ = ('BloodyCommand', 'command')


def command(name=None, **attrs):
    print(attrs)
    return dpy_commands.command(name=name, cls=BloodyCommand, **attrs)


class BloodyCommand(dpy_commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        print(kwargs)
        self.wants_db = kwargs.pop('wants_db', False)
