import typing

import lavalink
from lavalink import Node
from discord.enums import Enum, try_enum


class LoadType(Enum):
    TRACK_LOADED = 'TRACK_LOADED'
    PLAYLIST_LOADED = 'PLAYLIST_LOADED'
    SEARCH_RESULT = 'SEARCH_RESULT'
    NO_MATCHES = 'NO_MATCHES'
    LOAD_FAILED = 'LOAD_FAILED'


class PlaylistInfo:
    def __init__(self, **data):
        self.name = data.pop('name')
        self.selectedTrack = data.pop('selectedTrack')


class Track:
    def __init__(self, **data):
        self.track = data.get('track')
        info = data.get('info')
        self.identifier = info.get('identifier')
        self.isSeekable = info.get('isSeekable')
        self.author = info.get('author')
        self.length = info.get('length')
        self.isStream = info.get('isStream')
        self.position = info.get('position')
        self.title = info.get('title')
        self.uri = info.get('uri')

        self.raw = data


class FetchTracksException(Exception):
    def __init__(self, message, severity) -> None:
        self.severity = severity
        super().__init__(message)


class TracksResponse:
    def __init__(self, **data):
        self.load_type: LoadType = try_enum(LoadType, data.pop('loadType'))

        playlist_info_raw = data.pop('playlistInfo')
        self.playlist_info: typing.Optional[PlaylistInfo] = \
            PlaylistInfo(**playlist_info_raw) if playlist_info_raw != {} else None

        self.tracks: typing.List[Track] = [Track(**t) for t in data.pop('tracks')]


class Client(lavalink.Client):

    async def get_tracks(self, query: str, node: Node = None):
        resp = await super().get_tracks(query, node)
        # noinspection PySimplifyBooleanCheck
        if resp == []:
            raise Exception('An error occurred while loading tracks')

        if resp['loadType'] == 'LOAD_FAILED':
            exc = resp['exception']
            raise FetchTracksException(exc['message'], exc['severity'])

        return TracksResponse(**resp)
