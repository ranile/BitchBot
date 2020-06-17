import asyncio
import itertools
import re
import typing

import discord
import humanize
import lavalink
from discord.ext import commands as dpy_commands, menus
import util
from BitchBot import BitchBot
from util import commands, lavalink as mlavalink

URL_EXP = re.compile('https?://(?:www.)?.+')
ZWS = '\u200b'


def format_time(time: int) -> str:
    days, hours, minutes, seconds = lavalink.parse_time(time)
    formatted = []
    for i in (days, hours):
        if i != 0:
            formatted.append(f'{int(i)}:')
    formatted.append(f'{int(minutes)}:')
    formatted.append(f'{int(seconds)}')
    return ''.join(formatted)


class TrackSelectionMenu(menus.Menu):

    def __init__(self, *, tracks: typing.List[mlavalink.Track]):
        super().__init__(timeout=60.0, delete_message_after=True, check_embeds=True, message=None)
        self._tracks = {}
        emojis = list(util.EMOJI_CHARS.values())
        for i, track in enumerate(tracks[:5]):
            emoji = emojis[i]
            self._tracks[emoji] = track

            self.add_button(menus.Button(emoji, self.selection_button))

        self.add_button(menus.Button('<:stop:678961746869747739>', self.stop_button))

        self._selection: typing.Optional[mlavalink.Track] = None

    async def send_initial_message(self, ctx: commands.Context, _):
        desc = []
        for emoji, track in self._tracks.items():
            p = f'{emoji}: '
            desc.append(
                f'{p}[{track.title}]({track.uri}) - {track.author}\n'
                f'{util.space(len(p) + 4)}**Length**: {format_time(track.length)}')
        return await ctx.send(embed=discord.Embed(
            title='Select a song to play',
            description='\n'.join(desc),
            color=util.random_discord_color(),
        ))

    async def selection_button(self, payload: discord.RawReactionActionEvent):
        self._selection = self._tracks[str(payload.emoji)]
        self.stop()

    async def stop_button(self, _):
        self.stop()

    async def response(self, ctx: commands.Context) -> mlavalink.Track:
        await self.start(ctx, wait=True)
        return self._selection


def alone_or_has_perms():
    async def predicate(ctx: commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True

        m = [m for m in ctx.author.voice.channel.members if not m.bot]  # just checks for bot, i'm one after-all
        if len(m) == 1 and m[0].id == ctx.author.id:
            return True
        elif ctx.author.guild_permissions.manage_channels:
            return True
        else:
            raise dpy_commands.CheckFailure('You must be alone in the Voice Channel with bot '
                                            'or have Manage Channels permission to use this command')

    return dpy_commands.check(predicate)


def must_be_playing():
    def pred(ctx: commands.Context):
        if ctx.player is not None and ctx.player.is_playing:
            return True
        raise dpy_commands.CheckFailure('Music must be playing in order to use this command')

    return dpy_commands.check(pred)


def player_must_exist():
    def pred(ctx: commands.Context):
        if ctx.player is not None:
            return True
        raise dpy_commands.CheckFailure('There is no player for this server. Play some music and try again')

    return dpy_commands.check(pred)


# noinspection PyIncorrectDocstring
class Music(dpy_commands.Cog):

    def __init__(self, bot: BitchBot):
        self.bot: BitchBot = bot
        self.bot.loop.create_task(self.attach_hooks())

    async def attach_hooks(self):
        await self.bot.wait_until_ready()
        self.bot.lavalink.add_event_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.QueueEndEvent):
            to_sleep = 60

            await asyncio.sleep(to_sleep)
            if len(event.player.queue) == 0 and event.player.current is None:
                await self.stop_player(int(event.player.guild_id))
                channel = self.bot.get_channel(int(event.player.fetch('channel')))
                my_voice = self.bot.get_guild(channel.guild.id).me.voice
                if my_voice and my_voice.channel:
                    await channel.send(f'Nothing has been played for the past {to_sleep} seconds '
                                       f'so I have decided to leave the voice channel')

    # noinspection PyProtectedMember
    async def connect_to(self, guild_id: int, channel_id: typing.Optional[int]):
        """ Connects to the given voice channel ID. A channel_id of `None` means disconnect. """

        # Internal attr, not typed
        # noinspection PyUnresolvedReferences
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id if channel_id is None else str(channel_id))

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        # noinspection PyProtectedMember
        self.bot.lavalink._event_hooks.clear()

    async def cog_check(self, ctx: commands.Context):

        if ctx.guild is None:
            raise dpy_commands.NoPrivateMessage('Music commands cannot be used in DMs')

        if ctx.author.voice is None and ctx.command.name not in (self.play.name, self.connect.name):
            raise dpy_commands.CheckFailure('You are not in a voice channel and no channel is provided')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        if not player.is_connected:
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise dpy_commands.BotMissingPermissions(['connect', 'speak'])

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise dpy_commands.CheckFailure('You need to be in my voice channel.')

    @dpy_commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, _):
        if before.channel is None or member.bot:
            return

        guild = member.guild
        if guild.me not in before.channel.members:
            return
        members = [m for m in before.channel.members if not m.bot]

        if len(members) == 0:
            await self.stop_player(guild.id)
            channel = self.bot.get_channel(int(self.bot.lavalink.player_manager.get(guild.id).fetch('channel')))
            await channel.send('All the humans has left the voice channel so I have decided to leave too')

    async def stop_player(self, guild_id: int):
        player = self.bot.lavalink.player_manager.get(guild_id)
        if player is None:
            return  # it doesn't exist so....

        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(guild_id, None)

    @commands.command()
    async def connect(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """
        Connect to a valid voice channel.

        Args:
            channel: The channel to connect to
        """
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            raise dpy_commands.CheckFailure('You must be in a Voice Channel to use this command '
                                            'or give me a channel to connect to')
        await self.connect_to(ctx.guild.id, channel.id)
        await ctx.send(f'Connected to **{channel}**')

    @commands.command()
    @dpy_commands.max_concurrency(1, dpy_commands.BucketType.guild)
    async def play(self, ctx: commands.Context, *, query: str):
        """
        Add a song to the queue.

        Args:
            query: The search query. Can also be a URL
        """

        await ctx.trigger_typing()

        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not URL_EXP.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results: mlavalink.TracksResponse = await ctx.player.node.get_tracks(query)

        # noinspection PyPep8Naming
        LoadType = mlavalink.LoadType
        if results.load_type == LoadType.NO_MATCHES:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=util.random_discord_color())

        if results.load_type == LoadType.PLAYLIST_LOADED:
            tracks = results.tracks

            for track in tracks:
                ctx.player.add(requester=ctx.author.id, track=track.raw)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'

        elif results.load_type == LoadType.TRACK_LOADED:
            track = results.tracks[0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track.title}]({track.uri})'

            ctx.player.add(requester=ctx.author.id, track=track.raw)

        elif results.load_type == LoadType.SEARCH_RESULT:
            track = await TrackSelectionMenu(tracks=results.tracks).response(ctx)
            if track is None:
                return await ctx.send('You did not pick anything')
            embed.title = 'Track Enqueued'
            embed.description = f'[{track.title}]({track.uri})'
            ctx.player.add(requester=ctx.author.id, track=track.raw)
        else:
            return  # in case shit goes down

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not ctx.player.is_playing:
            await ctx.player.play()

    @commands.command()
    @alone_or_has_perms()
    @must_be_playing()
    async def repeat(self, ctx: commands.Context):
        """Puts the player on repeat"""

        ctx.player.repeat = not ctx.player.repeat
        await ctx.send(f'Set repeat to: {ctx.player.repeat}')

    @commands.command()
    @alone_or_has_perms()
    @must_be_playing()
    async def pause(self, ctx: commands.Context):
        """Pause the player."""
        if ctx.player.paused:
            return await ctx.send('Already paused!')
        await ctx.player.set_pause(True)
        await ctx.send('Paused!')

    @commands.command()
    @alone_or_has_perms()
    async def resume(self, ctx: commands.Context):
        """Resume the player from a paused state."""

        if not ctx.player.paused:
            return await ctx.send('I am not currently paused!')

        await ctx.send('Resuming the player!')
        await ctx.player.set_pause(False)

    @commands.command()
    @alone_or_has_perms()
    @must_be_playing()
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""

        await ctx.player.skip()
        await ctx.send("Skipped!")

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    @must_be_playing()
    async def now_playing(self, ctx: commands.Context):
        """Retrieve the currently playing song."""

        current = ctx.player.current
        await ctx.send(embed=discord.Embed(
            title='Now playing',
            description=f'[{current.title}]({current.uri}) - {current.author}\n'
                        f'**Duration**: {format_time(ctx.player.position)} / {format_time(current.duration)}\n'
                        f'**Requested by**: {ctx.guild.get_member(current.requester).display_name}'
        ))

    @commands.command(aliases=['q'])
    @must_be_playing()
    async def queue(self, ctx: commands.Context):
        """Retrieve information on the next 5 songs from the queue."""
        upcoming = list(itertools.islice(ctx.player.queue, 0, 5))

        desc = []
        for song in upcoming:
            desc.append(
                f'[{song.title}]({song.uri}) - {song.author}\n'
                f'**Length**: {format_time(song.duration)}; {util.space(8)}'
                f'**Requested by**: {ctx.guild.get_member(song.requester).display_name}'
            )

        embed = discord.Embed(
            title=f'**Player queue**\n{len(upcoming)} upcoming',
            description='\n'.join(desc),
            color=util.random_discord_color()
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'dc'])
    @alone_or_has_perms()
    @must_be_playing()
    async def stop(self, ctx: commands.Context):
        """Stop and disconnect the player"""
        await self.stop_player(ctx.guild.id)
        await ctx.send('Stopped successfully')

    @commands.command(aliases=('lavalinkinfo', 'llinfo'))
    @player_must_exist()
    async def lavalink_info(self, ctx: commands.Context):
        """Retrieve various Node/Server/Player information."""

        stats = ctx.player.node.stats

        sp = util.space

        embed = discord.Embed(
            title=f'Stats for Lavalink node',
            color=util.random_discord_color(),
        ).add_field(
            name=f'**__Resource Consumption__**:',
            value=f'**Memory**:\n'
                  f'{sp(2)}**Used**: {humanize.naturalsize(stats.memory_used)}\n'
                  f'{sp(2)}**Total**: {humanize.naturalsize(stats.memory_allocated)}\n'
                  f'{sp(2)}**Free**: {humanize.naturalsize(stats.memory_free)}\n'
                  f'**CPU**:\n'
                  f'{sp(2)}**Cores used**: {stats.cpu_cores}',
            inline=False
        ).add_field(
            name='**__Players__**',
            value=f'**Total connected**: {stats.players}\n'
                  f'**Currently playing**: {stats.playing_players}',
            inline=False
        )
        uptime = lavalink.utils.parse_time(stats.uptime)
        units = ('days', 'hours', 'minutes', 'seconds')
        fmt = ', '.join([f'{int(val)} {units[i]}' for i, val in enumerate(uptime)])
        fmt = fmt.strip().replace('minutes,', 'minutes and')  # hacky but works
        node_manager = self.bot.lavalink.node_manager
        embed.add_field(
            name='**__Misc__**',
            value=f'**Uptime**: {fmt}\n'
                  f'**Nodes**:\n'
                  f'{sp(2)}**Total**: {len(node_manager.nodes)}\n'
                  f'{sp(2)}**Available**: {len(node_manager.available_nodes)}\n',
            inline=False
        )

        embed.set_footer(
            text=f'Using lavalink v{lavalink.__version__}',
            icon_url='https://serux.pro/9e83af1581.png'
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
