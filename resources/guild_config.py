from resources import Resource


class GuildConfig(Resource):
    def __init__(self, **kwargs):
        self.guild_id = kwargs.pop('guild_id')
        self.starboard_channel = kwargs.pop('starboard_channel', None)
        self.event_log_webhook = kwargs.pop('event_log_webhook', None)
        self.muted_role_id = kwargs.pop('mute_role_id', None)
        self.mod_roles = kwargs.pop('mod_roles', [])

    @classmethod
    def convert(cls, record):
        return cls(
            guild_id=record['guild_id'],
            starboard_channel=record['starboard_channel'],
            event_log_webhook=record['event_log_webhook'],
            mute_role_id=record['mute_role_id'],
            mod_roles=record['mod_roles'],
        )
