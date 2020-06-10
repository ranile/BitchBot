from discord.ext import commands as dpy_commands

__all__ = ('Command', 'command', 'group')


def command(name=None, **attrs):
    print(attrs)
    return dpy_commands.command(name=name, cls=Command, **attrs)


def group(name=None, **attrs):
    print('yes')
    attrs['cls'] = Group
    return dpy_commands.group(name=name, **attrs)


class Command(dpy_commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        print(kwargs)
        self.wants_db = kwargs.pop('wants_db', False)


class Group(dpy_commands.Group):
    def __init__(self, *args, **attrs):
        super().__init__(*args, **attrs)
        self.wants_db = attrs.pop('wants_db', False)

    def command(self, *args, **kwargs):
        kwargs['cls'] = Command
        return super().command(*args, **kwargs)

    def group(self, *args, **kwargs):
        print('yesg', kwargs)
        kwargs['cls'] = Group

        def decorator(func):
            kwargs.setdefault('parent', self)
            result = group(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator
