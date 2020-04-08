import asyncio
import datetime
import itertools
import re
from typing import Union

import discord
import humanize
import wavelink
from discord.ext import commands

import keys

URL_EXP = re.compile('https?://(?:www.)?.+')


def convert_from_ms(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    seconds = seconds + milliseconds / 1000
    h, m, s = int(hours + (days * 24)), int(minutes), int(seconds)

    def append_0_if_needed(val):
        return val if len(str(val)) > 1 else f'0{val}'

    return f"{f'{h}:' if h != 0 else ''}{append_0_if_needed(m)}:{append_0_if_needed(s)}"


class CannotManageMusic(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if message is None:
            message = "You must be alone in the Voice Channel with bot or has Manage Channels permission to " \
                      "use this command"
        super().__init__(message, *args)


class MustBeInVoiceException(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if message is None:
            message = "You must be in a Voice Channel to use this command"
        super().__init__(message, *args)


class NoControllerFound(commands.CommandError):
    pass


def alone_or_has_perms():
    def predicate(ctx):
        m = [m for m in ctx.author.voice.channel.members if not m.id == ctx.me.id]
        if len(m) == 1 and m[0].id == ctx.author.id:
            return True
        elif ctx.author.guild_permissions.manage_channels:
            return True
        else:
            raise CannotManageMusic

    return commands.check(predicate)


class BloodyPlayer(wavelink.Player):

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], guild_id: int, node, **kwargs):
        super().__init__(bot, guild_id, node, **kwargs)
        self.on_repeat = kwargs.pop('on_repeat', False)


class BloodyWavelinkClient(wavelink.Client):

    def get_player(self, guild_id: int, *, cls=None, node_id=None, **kwargs) -> BloodyPlayer:
        return super().get_player(guild_id, cls=BloodyPlayer, node_id=node_id, **kwargs)


class MusicController:

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.context = ctx

        self.next = asyncio.Event()
        self._queue = asyncio.Queue()

        self.current = None
        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.context.guild.id)

        while True:
            self.next.clear()
            if self.current is not None and player.on_repeat:
                song = self.current
            else:
                self.current = song = await self._queue.get()
            await player.play(song)
            await self.context.send(f'Now playing: `{song}`')

            await self.next.wait()

    async def add_to_queue(self, track, *, should_set):
        await self._queue.put(track)
        if should_set:
            self.next.set()
            player = self.bot.wavelink.get_player(self.context.guild.id)
            player.on_repeat = False

    def get_current_queue(self):
        return list(self._queue._queue)


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = BloodyWavelinkClient(self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        node = await self.bot.wavelink.initiate_node(
            host='localhost',
            port=2333,
            rest_uri='http://localhost:2333',
            password=keys.lavalink_pass,
            identifier='DEBUG',
            region='us_central'
        )

        # Set our node hook callback
        node.set_hook(self.on_event_hook)

    async def on_event_hook(self, event):
        """Node hook callback."""
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        members = [m for m in before.channel.members if not m.id == guild.me.id]
        if len(members) == 0:
            ctx = self.get_controller(member.guild).context
            await self.stop_player(guild)
            await ctx.send('Everyone has left the voice channel so I have decided to leave too')

    def get_controller(self, value: Union[commands.Context, wavelink.Player, discord.Guild]):
        if isinstance(value, commands.Context):
            gid = value.guild.id
        elif isinstance(value, discord.Guild):
            gid = value.id
        else:
            gid = value.guild_id

        try:
            return self.controllers[gid]
        except KeyError as e:
            raise NoControllerFound(
                "No MusicController was found for this server. Stopping and reconnecting should fix this") from e

    async def stop_player(self, guild):
        player = self.bot.wavelink.get_player(guild.id)
        try:
            del self.controllers[guild.id]
        except KeyError:
            pass

        await player.disconnect()

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        if ctx.author.voice is None and ctx.command.name not in (self.play.name, self.connect.name):
            raise MustBeInVoiceException
        return True

    async def connect_to_channel(self, ctx, channel=None):
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise MustBeInVoiceException('No valid voice channel specified and author is not in one.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        self.controllers[ctx.guild.id] = MusicController(ctx)
        await player.connect(channel.id)

    @commands.command()
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        """
        Connect to a valid voice channel.

        Args:
            channel: The channel to connect to
        """
        await self.connect_to_channel(ctx, channel)
        await ctx.send(f'Connected to **{channel}**')

    @commands.command()
    async def play(self, ctx, *, query: str):
        """
        Add a song to the queue.

        Args:
            query: The search query. Can also be a URL
        """
        if not URL_EXP.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(f'{query}')

        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await self.connect_to_channel(ctx)

        track = tracks[0]
        # TODO: Add track picker menu

        controller = self.get_controller(ctx)
        await controller.add_to_queue(track, should_set=not player.is_playing)

        await ctx.send(f'Added {str(track)} to the queue.')

    @commands.command()
    @alone_or_has_perms()
    async def repeat(self, ctx):
        """Puts the player on repeat"""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        player.on_repeat = not player.on_repeat
        await ctx.send(f'Set repeat to {player.on_repeat}')

    @commands.command()
    @alone_or_has_perms()
    async def pause(self, ctx):
        """Pause the player."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('I am not currently playing anything!')

        await ctx.send('Pausing the song!')
        await player.set_pause(True)

    @commands.command()
    @alone_or_has_perms()
    async def resume(self, ctx):
        """Resume the player from a paused state."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send('I am not currently paused!')

        await ctx.send('Resuming the player!')
        await player.set_pause(False)

    @commands.command()
    @alone_or_has_perms()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('I am not currently playing anything!')

        await ctx.send('Skipping the song!')
        await player.stop()

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    async def now_playing(self, ctx):
        """Retrieve the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        current = player.current

        await ctx.send(f'Now playing: {current}\n'
                       f'{convert_from_ms(player.position)} / {convert_from_ms(current.length)}')

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Retrieve information on the next 5 songs from the queue."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        queue = controller.get_current_queue()
        if not player.current or len(queue) == 0:
            return await ctx.send('There are no songs currently in the queue.')

        upcoming = list(itertools.islice(queue, 0, 5))

        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}')
        for song in upcoming:
            embed.add_field(name=str(song), value=f"**Length**: {convert_from_ms(song.length)}\n"
                                                  f"{f'**URL**: [Link]({song.uri})' if song.uri else ''}")

        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'dc'])
    @alone_or_has_perms()
    async def stop(self, ctx):
        """Stop and disconnect the player"""
        await self.stop_player(ctx.guild)
        await ctx.send('Stopped successfully')

    @commands.command(aliases=('lavalinkinfo', 'llinfo'))
    async def lavalink_info(self, ctx):
        """Retrieve various Node/Server/Player information."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores

        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
              f'`{node.stats.players}` players are distributed on server.\n' \
              f'`{node.stats.playing_players}` players are playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}`\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)


def setup(bot):
    bot.add_cog(Music(bot))