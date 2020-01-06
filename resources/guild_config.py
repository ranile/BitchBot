from resources import Resource


class GuildConfig(Resource):
    def __init__(self, **kwargs):
        self.guild_id = kwargs.pop('guild_id')
        self.starboard_channel = kwargs.pop('starboard_channel')
        self.event_log_webhook = kwargs.pop('event_log_webhook')
        self.muted_role_id = kwargs.pop('mute_role_id')

    @classmethod
    def convert(cls, record):
        return cls(
            guild_id=record['guild_id'],
            starboard_channel=record['starboard_channel'],
            event_log_webhook=record['event_log_webhook'],
            mute_role_id=record['mute_role_id']
        )
