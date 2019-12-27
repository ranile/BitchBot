from resources import Resource


class GuildConfig(Resource):
    def __init__(self, **kwargs):
        self.guild_id = kwargs.pop('guild_id')
        self.starboard_channel = kwargs.pop('starboard_channel')

    @classmethod
    def convert(cls, record):
        return cls(
            guild_id=record['guild_id'],
            starboard_channel=record['starboard_channel']
        )
