import asyncio
import itertools
import re
import discord
import humanize
import lavalink
from discord.ext import commands
import keys
import util

URL_EXP = re.compile('https?://(?:www.)?.+')
ZWS = '\u200b'


class CannotManageMusic(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if message is None:
            message = "You must be alone in the Voice Channel with bot " \
                      "or have Manage Channels permission to use this command"
        super().__init__(message, *args)


class MustBeInVoiceException(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if message is None:
            message = "You must be in a Voice Channel to use this command"
        super().__init__(message, *args)


def alone_or_has_perms():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True

        m = [m for m in ctx.author.voice.channel.members if not m.bot]  # just checks for bot, i'm one after-all
        if len(m) == 1 and m[0].id == ctx.author.id:
            return True
        elif ctx.author.guild_permissions.manage_channels:
            return True
        else:
            raise CannotManageMusic

    return commands.check(predicate)


def must_be_playing():
    def pred(ctx):
        player = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
        if player is not None and player.is_playing:
            return True
        raise commands.CheckFailure('Music must be playing in order to use this command')

    return commands.check(pred)


# noinspection PyIncorrectDocstring
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.create_node())

    async def create_node(self):
        await self.bot.wait_until_ready()

        if not hasattr(self.bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node('127.0.0.1', 2333, keys.lavalink_pass, 'eu',
                                       'default-node')  # Host, Port, Password, Region, Name
            self.bot.add_listener(self.bot.lavalink.voice_update_handler, 'on_socket_response')

        self.bot.lavalink.add_event_hook(self.track_hook)

    async def track_hook(self, event):
        if isinstance(event, lavalink.QueueEndEvent):
            to_sleep = 60

            await asyncio.sleep(to_sleep)
            if len(event.player.queue) == 0 and event.player.current is None:
                await self.stop_player(int(event.player.guild_id))
                channel = self.bot.get_channel(int(event.player.fetch('channel')))
                await channel.send(f'Nothing has been played for the past {to_sleep} seconds '
                                   f'so I have decided to leave the voice channel')

    # noinspection PyProtectedMember
    async def connect_to(self, guild_id: int, channel_id):
        """ Connects to the given voice channel ID. A channel_id of `None` means disconnect. """

        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    # noinspection PyProtectedMember
    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if ctx.guild is None:
            raise commands.NoPrivateMessage

        if ctx.author.voice is None and ctx.command.name not in (self.play.name, self.connect.name):
            raise MustBeInVoiceException('You are not in a voice channel and no channel is provided')

        return True

    async def cog_before_invoke(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        if not player.is_connected:
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.BotMissingPermissions('connect', 'speak')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise MustBeInVoiceException('You need to be in my voice channel.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, _after):
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

    async def stop_player(self, guild_id):
        player = self.bot.lavalink.player_manager.get(guild_id)
        if player is None:
            return  # it doesn't exist so....

        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(guild_id, None)

    @commands.command()
    async def connect(self, ctx, *, channel: discord.VoiceChannel = None):
        """
        Connect to a valid voice channel.

        Args:
            channel: The channel to connect to
        """
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            raise MustBeInVoiceException
        await self.connect_to(ctx.guild.id, channel.id)
        await ctx.send(f'Connected to **{channel}**')

    @commands.command()
    async def play(self, ctx, *, query: str):
        """
        Add a song to the queue.

        Args:
            query: The search query. Can also be a URL
        """
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not URL_EXP.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        if results['loadType'] == 'NO_MATCHES':
            return await ctx.send('Nothing found!')
        elif results['loadType'] == 'LOAD_FAILED':
            raise commands.CommandError(results['exception']['message'])

        embed = discord.Embed(color=util.random_discord_color())

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        elif results['loadType'] in ('TRACK_LOADED', 'SEARCH_RESULT'):

            track = results['tracks'][0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            player.add(requester=ctx.author.id, track=track)
        else:
            raise Exception

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @commands.command()
    @alone_or_has_perms()
    @must_be_playing()
    async def repeat(self, ctx):
        """Puts the player on repeat"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.repeat = not player.repeat
        await ctx.send(f'Set repeat to: {player.repeat}')

    @commands.command()
    @alone_or_has_perms()
    async def pause(self, ctx):
        """Pause the player."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        print(player.paused)
        if player.paused:
            return await ctx.send('Already paused!')
        await player.set_pause(True)
        await ctx.send('Paused!')

    @commands.command()
    @alone_or_has_perms()
    async def resume(self, ctx):
        """Resume the player from a paused state."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.paused:
            return await ctx.send('I am not currently paused!')

        await ctx.send('Resuming the player!')
        await player.set_pause(False)

    @commands.command()
    @alone_or_has_perms()
    @must_be_playing()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await player.skip()
        await ctx.send("Skipped!")

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    @must_be_playing()
    async def now_playing(self, ctx):
        """Retrieve the currently playing song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        current = player.current
        await ctx.send(f'Now playing: {current.title}\n'
                       f'{lavalink.format_time(player.position)} / {lavalink.format_time(current.duration)}')

    @commands.command(aliases=['q'])
    @must_be_playing()
    async def queue(self, ctx):
        """Retrieve information on the next 5 songs from the queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        upcoming = list(itertools.islice(player.queue, 0, 5))

        embed = discord.Embed(title=f'Player queue', description=f'**{len(upcoming)} upcoming**')
        for song in upcoming:
            embed.add_field(name=song.title, value=f"**Length**: {lavalink.format_time(song.duration)}\n"
                                                   f"{f'**URL**: [Link]({song.uri})' if song.uri else ''}")

        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'dc'])
    @alone_or_has_perms()
    @must_be_playing()
    async def stop(self, ctx):
        """Stop and disconnect the player"""
        await self.stop_player(ctx.guild.id)
        await ctx.send('Stopped successfully')

    @commands.command(aliases=('lavalinkinfo', 'llinfo'))
    async def lavalink_info(self, ctx):
        """Retrieve various Node/Server/Player information."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player is None:
            raise commands.CommandError('The bot must be playing something for this command to be used')

        stats = player.node.stats

        def space(count=4):
            return f'{ZWS} ' * count

        embed = discord.Embed(
            title=f'Stats for Lavalink node',
            color=util.random_discord_color(),
        )
        embed.add_field(
            name=f'**__Resource Consumption__**:',
            value=f'**Memory**:\n'
                  f'{space(2)}**Used**: {humanize.naturalsize(stats.memory_used)}\n'
                  f'{space(2)}**Total**: {humanize.naturalsize(stats.memory_allocated)}\n'
                  f'{space(2)}**Free**: {humanize.naturalsize(stats.memory_free)}\n'
                  f'**CPU**:\n'
                  f'{space(2)}**Cores used**: {stats.cpu_cores}',
            inline=False
        )
        embed.add_field(
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
                  f'{space(2)}**Total**: {len(node_manager.nodes)}\n'
                  f'{space(2)}**Available**: {len(node_manager.available_nodes)}\n',
            inline=False
        )

        embed.set_footer(
            text=f'Using lavalink v{lavalink.__version__}',
            icon_url='https://serux.pro/9e83af1581.png'
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
